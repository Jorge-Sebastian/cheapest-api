#!/usr/bin/env python3
"""Ejecutor asíncrono para las cargas mayores a 450 usuarios del laboratorio 2."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import time
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import aiohttp


GET_PATH = "/logistics/tenderos/productos-disponibles"
POST_PATH = "/logistics/pedidos"


@dataclass
class Result:
    timestamp_iso: str
    method: str
    endpoint: str
    status_code: int
    latency_ms: float
    error: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prueba de carga asíncrona de Cheapest")
    parser.add_argument("--endpoint", required=True, choices=("GET", "POST"), type=str.upper)
    parser.add_argument("--users", required=True, type=int, help="Concurrencia máxima")
    parser.add_argument("--ramp-up", required=True, type=float, help="Ramp-up en segundos")
    parser.add_argument("--duration", required=True, type=float, help="Duración total en segundos")
    parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Solicitudes por usuario; 0 repite hasta completar duration",
    )
    parser.add_argument("--output", required=True, type=Path, help="CSV de salida")
    parser.add_argument("--base-url", default="http://localhost:3000")
    parser.add_argument("--body", type=Path, help="Plantilla JSON obligatoria para POST")
    parser.add_argument("--tienda-id", default="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    parser.add_argument("--zona", default="Zona Norte")
    parser.add_argument("--timeout", type=float, default=10.0, help="Timeout por solicitud")
    args = parser.parse_args()
    if (
        args.users <= 0
        or args.ramp_up < 0
        or args.duration <= 0
        or args.timeout <= 0
        or args.iterations < 0
    ):
        parser.error("users y duration deben ser positivos; ramp-up no puede ser negativo")
    if args.endpoint == "POST" and args.body is None:
        parser.error("--body es obligatorio para POST")
    if args.output.exists():
        parser.error(f"el resultado ya existe y no será sobrescrito: {args.output}")
    return args


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]


def load_body(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with path.open(encoding="utf-8") as handle:
        body = json.load(handle)
    items = body.get("items", [])
    if len(items) <= 20:
        raise ValueError("el cuerpo POST debe contener más de 20 ítems")
    return body


def post_body(template: dict[str, Any]) -> dict[str, Any]:
    body = deepcopy(template)
    body["identificador"] = f"LOAD-{uuid.uuid4()}"
    body["fechaHoraCreacion"] = datetime.now(timezone.utc).isoformat()
    return body


async def request_once(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    body_template: dict[str, Any] | None,
) -> Result:
    started_wall = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    status = 0
    error = ""
    try:
        payload = post_body(body_template) if body_template is not None else None
        async with session.request(method, url, json=payload) as response:
            status = response.status
            await response.read()
            if status >= 400:
                error = f"HTTP {status}"
    except asyncio.TimeoutError:
        error = "timeout"
    except aiohttp.ClientError as exc:
        error = f"{type(exc).__name__}: {exc}"
    latency_ms = (time.perf_counter() - started) * 1000
    return Result(started_wall, method, url, status, latency_ms, error)


async def virtual_user(
    user_id: int,
    args: argparse.Namespace,
    session: aiohttp.ClientSession,
    url: str,
    body_template: dict[str, Any] | None,
    deadline: float,
    results: list[Result],
) -> None:
    delay = args.ramp_up * user_id / args.users
    await asyncio.sleep(delay)
    if args.iterations:
        for _ in range(args.iterations):
            if time.perf_counter() >= deadline:
                break
            results.append(await request_once(session, args.endpoint, url, body_template))
    else:
        while time.perf_counter() < deadline:
            results.append(await request_once(session, args.endpoint, url, body_template))


async def run(args: argparse.Namespace) -> tuple[list[Result], float]:
    body_template = load_body(args.body)
    base_url = args.base_url.rstrip("/")
    if args.endpoint == "GET":
        query = urlencode({"tiendaId": args.tienda_id, "zona": args.zona})
        url = f"{base_url}{GET_PATH}?{query}"
    else:
        url = f"{base_url}{POST_PATH}"

    timeout = aiohttp.ClientTimeout(total=args.timeout)
    connector = aiohttp.TCPConnector(limit=args.users, ttl_dns_cache=300)
    results: list[Result] = []
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        health_url = f"{base_url}/health"
        try:
            async with session.get(health_url) as response:
                await response.read()
                if response.status != 200:
                    raise RuntimeError(
                        f"la API no está saludable: {health_url} respondió HTTP {response.status}"
                    )
        except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
            raise RuntimeError(
                f"la API no está disponible en {health_url}: {exc}"
            ) from exc

        started = time.perf_counter()
        deadline = started + args.duration
        tasks = [
            asyncio.create_task(
                virtual_user(i, args, session, url, body_template, deadline, results)
            )
            for i in range(args.users)
        ]
        await asyncio.gather(*tasks)
    return results, time.perf_counter() - started


def write_csv(path: Path, results: list[Result]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("timestamp_iso", "method", "endpoint", "status_code", "latency_ms", "error"))
        for item in results:
            writer.writerow(
                (item.timestamp_iso, item.method, item.endpoint, item.status_code,
                 f"{item.latency_ms:.3f}", item.error)
            )


def print_summary(args: argparse.Namespace, results: list[Result], elapsed: float) -> None:
    if not results:
        raise RuntimeError("no se ejecutaron solicitudes; duration debe superar el ramp-up inicial")
    latencies = [item.latency_ms for item in results]
    errors = sum(item.status_code >= 400 or item.status_code == 0 or bool(item.error) for item in results)
    total = len(results)
    print("\n=== RESUMEN FINAL ===")
    print(f"Método:             {args.endpoint}")
    print(f"Total solicitudes:  {total}")
    print(f"Duración real:      {elapsed:.3f} s")
    print(f"Throughput:         {total / elapsed:.2f} req/s")
    print(f"Latencia promedio:  {sum(latencies) / total:.2f} ms")
    print(f"Latencia p95:       {percentile(latencies, 0.95):.2f} ms")
    print(f"Latencia p99:       {percentile(latencies, 0.99):.2f} ms")
    print(f"Errores:            {errors} ({errors * 100 / total:.2f}%)")
    print(f"Resultado CSV:      {args.output}")


def main() -> None:
    args = parse_args()
    try:
        results, elapsed = asyncio.run(run(args))
        write_csv(args.output, results)
        print_summary(args, results, elapsed)
    except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main()

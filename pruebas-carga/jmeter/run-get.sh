#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 5 ]; then
  echo "Uso: $0 <escenario> <corrida> <usuarios> <ramp-up-segundos> <loops>"
  echo "Ejemplo: $0 smoke 1 5 5 1"
  exit 1
fi

scenario="$1"
run_number="$2"
users="$3"
ramp_up="$4"
loops="$5"

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "${script_dir}/../.." && pwd)"
result_dir="${project_dir}/pruebas-carga/resultados/jmeter/get/${scenario}"
run_padded="$(printf '%02d' "${run_number}")"
result_file="${result_dir}/pareto_get_${scenario}_run${run_padded}.jtl"
log_file="${result_dir}/pareto_get_${scenario}_run${run_padded}.log"
test_plan="${script_dir}/get-productos-disponibles.jmx"

if command -v jmeter >/dev/null 2>&1; then
  jmeter_bin="$(command -v jmeter)"
else
  jmeter_bin="${HOME}/Downloads/apache-jmeter-5.6.3/bin/jmeter"
fi

if [ ! -x "${jmeter_bin}" ]; then
  echo "No se encontró JMeter en: ${jmeter_bin}"
  echo "Instale JMeter o agregue su ejecutable al PATH."
  exit 1
fi

if ! curl -fsS http://localhost:3000/health >/dev/null; then
  echo "La API no responde correctamente en http://localhost:3000/health"
  exit 1
fi

if [ -e "${result_file}" ] || [ -e "${log_file}" ]; then
  echo "La corrida ya existe y no será sobrescrita:"
  echo "${result_file}"
  exit 1
fi

mkdir -p "${result_dir}"

echo "Ejecutando GET ${scenario}, corrida ${run_padded}"
echo "Usuarios=${users}, ramp-up=${ramp_up}s, loops=${loops}"
echo "Resultado=${result_file}"

"${jmeter_bin}" \
  -n \
  -t "${test_plan}" \
  -Jusers="${users}" \
  -Jramp_up="${ramp_up}" \
  -Jloops="${loops}" \
  -l "${result_file}" \
  -j "${log_file}"

echo "Corrida finalizada correctamente."

import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateTiendaDto, TiendaResponseDto, UpdateTiendaDto } from '../dtos';
import { TiendaRepository } from '../repositories';
import { Tienda } from '../repositories/entities';

@Injectable()
export class TiendaService {
  constructor(private readonly tiendaRepository: TiendaRepository) {}

  async create(dto: CreateTiendaDto): Promise<TiendaResponseDto> {
    const tienda = await this.tiendaRepository.create(dto);
    return this.mapToResponse(tienda);
  }

  async findAll(): Promise<TiendaResponseDto[]> {
    const tiendas = await this.tiendaRepository.findAll();
    return tiendas.map((tienda) => this.mapToResponse(tienda));
  }

  async findById(id: string): Promise<TiendaResponseDto> {
    const tienda = await this.tiendaRepository.findById(id);
    if (!tienda) {
      throw new NotFoundException(`Tienda con id ${id} no encontrada`);
    }
    return this.mapToResponse(tienda);
  }

  async exists(id: string): Promise<boolean> {
    return this.tiendaRepository.exists(id);
  }

  async update(id: string, dto: UpdateTiendaDto): Promise<TiendaResponseDto> {
    const tienda = await this.tiendaRepository.findById(id);
    if (!tienda) {
      throw new NotFoundException(`Tienda con id ${id} no encontrada`);
    }

    const tiendaActualizada = await this.tiendaRepository.update(id, dto);
    return this.mapToResponse(tiendaActualizada!);
  }

  async delete(id: string): Promise<void> {
    const tienda = await this.tiendaRepository.findById(id);
    if (!tienda) {
      throw new NotFoundException(`Tienda con id ${id} no encontrada`);
    }

    await this.tiendaRepository.delete(id);
  }

  private mapToResponse(tienda: Tienda): TiendaResponseDto {
    return {
      id: tienda.id,
      codigoInterno: tienda.codigoInterno,
      nombreComercial: tienda.nombreComercial,
      responsableUsuarioId: tienda.responsableUsuarioId,
      rut: tienda.rut,
      direccion: tienda.direccion,
      telefono: tienda.telefono,
      paisId: tienda.paisId,
      estadoCaptacion: tienda.estadoCaptacion,
      createdAt: tienda.createdAt,
      updatedAt: tienda.updatedAt,
    };
  }
}

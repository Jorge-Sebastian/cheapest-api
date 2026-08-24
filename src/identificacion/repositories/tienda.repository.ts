import { Inject, Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { Tienda } from './entities';

@Injectable()
export class TiendaRepository {
  constructor(
    @Inject('TIENDA_REPOSITORY')
    private readonly repository: Repository<Tienda>,
  ) {}

  async create(tienda: Partial<Tienda>): Promise<Tienda> {
    const nuevaTienda = this.repository.create(tienda);
    return this.repository.save(nuevaTienda);
  }

  async findAll(): Promise<Tienda[]> {
    return this.repository.find();
  }

  async findById(id: string): Promise<Tienda | null> {
    return this.repository.findOne({ where: { id } });
  }

  async exists(id: string): Promise<boolean> {
    return this.repository.existsBy({ id });
  }

  async update(id: string, cambios: Partial<Tienda>): Promise<Tienda | null> {
    await this.repository.update(id, cambios);
    return this.findById(id);
  }

  async delete(id: string): Promise<boolean> {
    const resultado = await this.repository.delete(id);
    return (resultado.affected ?? 0) > 0;
  }
}

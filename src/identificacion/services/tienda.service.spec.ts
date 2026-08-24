import { NotFoundException } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import { CreateTiendaDto } from '../dtos';
import { TiendaRepository } from '../repositories';
import { EstadoCaptacion, Tienda } from '../repositories/entities';
import { TiendaService } from './tienda.service';

describe('TiendaService', () => {
  let service: TiendaService;
  let repository: jest.Mocked<TiendaRepository>;

  const tiendaId = 'f95f119b-d7ba-41c9-84d9-020ab13447eb';

  const createDto: CreateTiendaDto = {
    codigoInterno: 'TDA-001',
    nombreComercial: 'Tienda El Vecino',
    responsableUsuarioId: '7703e25a-2119-493f-82a6-cf82b94db5c9',
    rut: '900123456-1',
    direccion: 'Calle 10 # 20-30',
    telefono: '+57 3001234567',
    paisId: 'e2777aac-a70e-4111-a0ec-d3054d09cb26',
  };

  const tienda: Tienda = {
    id: tiendaId,
    ...createDto,
    estadoCaptacion: EstadoCaptacion.PROSPECTO_CREADO,
    createdAt: new Date('2026-08-23T10:00:00Z'),
    updatedAt: new Date('2026-08-23T10:00:00Z'),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TiendaService,
        {
          provide: TiendaRepository,
          useValue: {
            create: jest.fn(),
            findAll: jest.fn(),
            findById: jest.fn(),
            exists: jest.fn(),
            update: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get(TiendaService);
    repository = module.get(TiendaRepository);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  it('should create a tienda', async () => {
    repository.create.mockResolvedValue(tienda);

    const result = await service.create(createDto);

    expect(repository.create).toHaveBeenCalledWith(createDto);
    expect(result).toEqual(tienda);
  });

  it('should return all tiendas', async () => {
    repository.findAll.mockResolvedValue([tienda]);

    await expect(service.findAll()).resolves.toEqual([tienda]);
  });

  it('should return a tienda by id', async () => {
    repository.findById.mockResolvedValue(tienda);

    await expect(service.findById(tiendaId)).resolves.toEqual(tienda);
  });

  it('should throw when a tienda is not found', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.findById(tiendaId)).rejects.toThrow(NotFoundException);
  });

  it('should return whether a tienda exists', async () => {
    repository.exists.mockResolvedValue(true);

    await expect(service.exists(tiendaId)).resolves.toBe(true);
    expect(repository.exists).toHaveBeenCalledWith(tiendaId);
  });

  it('should update an existing tienda', async () => {
    const tiendaActualizada = { ...tienda, telefono: '+57 3017654321' };
    repository.findById.mockResolvedValue(tienda);
    repository.update.mockResolvedValue(tiendaActualizada);

    const result = await service.update(tiendaId, {
      telefono: '+57 3017654321',
    });

    expect(repository.update).toHaveBeenCalledWith(tiendaId, {
      telefono: '+57 3017654321',
    });
    expect(result.telefono).toBe('+57 3017654321');
  });

  it('should not update a tienda that does not exist', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.update(tiendaId, {})).rejects.toThrow(
      NotFoundException,
    );
    expect(repository.update).not.toHaveBeenCalled();
  });

  it('should delete an existing tienda', async () => {
    repository.findById.mockResolvedValue(tienda);
    repository.delete.mockResolvedValue(true);

    await service.delete(tiendaId);

    expect(repository.delete).toHaveBeenCalledWith(tiendaId);
  });

  it('should not delete a tienda that does not exist', async () => {
    repository.findById.mockResolvedValue(null);

    await expect(service.delete(tiendaId)).rejects.toThrow(NotFoundException);
    expect(repository.delete).not.toHaveBeenCalled();
  });
});

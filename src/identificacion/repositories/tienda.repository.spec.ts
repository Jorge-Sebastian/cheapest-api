import { Test, TestingModule } from '@nestjs/testing';
import { Repository } from 'typeorm';
import { EstadoCaptacion, Tienda } from './entities';
import { TiendaRepository } from './tienda.repository';

describe('TiendaRepository', () => {
  let repository: TiendaRepository;
  let typeormRepository: jest.Mocked<Repository<Tienda>>;

  const tienda = {
    id: 'f95f119b-d7ba-41c9-84d9-020ab13447eb',
    codigoInterno: 'TDA-001',
    nombreComercial: 'Tienda El Vecino',
    responsableUsuarioId: '7703e25a-2119-493f-82a6-cf82b94db5c9',
    rut: '900123456-1',
    direccion: 'Calle 10 # 20-30',
    telefono: '+57 3001234567',
    paisId: 'e2777aac-a70e-4111-a0ec-d3054d09cb26',
    estadoCaptacion: EstadoCaptacion.PROSPECTO_CREADO,
    createdAt: new Date(),
    updatedAt: new Date(),
  } as Tienda;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        TiendaRepository,
        {
          provide: 'TIENDA_REPOSITORY',
          useValue: {
            create: jest.fn(),
            save: jest.fn(),
            find: jest.fn(),
            findOne: jest.fn(),
            existsBy: jest.fn(),
            update: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    repository = module.get(TiendaRepository);
    typeormRepository = module.get('TIENDA_REPOSITORY');
  });

  it('should create and save a tienda', async () => {
    typeormRepository.create.mockReturnValue(tienda);
    typeormRepository.save.mockResolvedValue(tienda);

    await expect(repository.create(tienda)).resolves.toEqual(tienda);
    expect(typeormRepository.save).toHaveBeenCalledWith(tienda);
  });

  it('should return all tiendas', async () => {
    typeormRepository.find.mockResolvedValue([tienda]);

    await expect(repository.findAll()).resolves.toEqual([tienda]);
  });

  it('should find a tienda by id', async () => {
    typeormRepository.findOne.mockResolvedValue(tienda);

    await expect(repository.findById(tienda.id)).resolves.toEqual(tienda);
    expect(typeormRepository.findOne).toHaveBeenCalledWith({
      where: { id: tienda.id },
    });
  });

  it('should check whether a tienda exists', async () => {
    typeormRepository.existsBy.mockResolvedValue(true);

    await expect(repository.exists(tienda.id)).resolves.toBe(true);
  });

  it('should update and return a tienda', async () => {
    typeormRepository.update.mockResolvedValue({ affected: 1 } as never);
    typeormRepository.findOne.mockResolvedValue(tienda);

    await expect(
      repository.update(tienda.id, { telefono: tienda.telefono }),
    ).resolves.toEqual(tienda);
  });

  it('should report whether a tienda was deleted', async () => {
    typeormRepository.delete.mockResolvedValue({ affected: 1 } as never);

    await expect(repository.delete(tienda.id)).resolves.toBe(true);
  });
});

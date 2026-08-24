import { Test, TestingModule } from '@nestjs/testing';
import { CreateTiendaDto, UpdateTiendaDto } from '../dtos';
import { EstadoCaptacion } from '../repositories/entities';
import { TiendaService } from '../services';
import { TiendaController } from './tienda.controller';

describe('TiendaController', () => {
  let controller: TiendaController;
  let service: jest.Mocked<TiendaService>;

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
  const response = {
    id: tiendaId,
    ...createDto,
    estadoCaptacion: EstadoCaptacion.PROSPECTO_CREADO,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [TiendaController],
      providers: [
        {
          provide: TiendaService,
          useValue: {
            create: jest.fn(),
            findAll: jest.fn(),
            findById: jest.fn(),
            update: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get(TiendaController);
    service = module.get(TiendaService);
  });

  it('should create a tienda', async () => {
    service.create.mockResolvedValue(response);

    await expect(controller.create(createDto)).resolves.toEqual(response);
    expect(service.create).toHaveBeenCalledWith(createDto);
  });

  it('should return all tiendas', async () => {
    service.findAll.mockResolvedValue([response]);

    await expect(controller.findAll()).resolves.toEqual([response]);
  });

  it('should return a tienda by id', async () => {
    service.findById.mockResolvedValue(response);

    await expect(controller.findById(tiendaId)).resolves.toEqual(response);
    expect(service.findById).toHaveBeenCalledWith(tiendaId);
  });

  it('should update a tienda', async () => {
    const dto: UpdateTiendaDto = { telefono: '+57 3017654321' };
    const updated = { ...response, ...dto };
    service.update.mockResolvedValue(updated);

    await expect(controller.update(tiendaId, dto)).resolves.toEqual(updated);
    expect(service.update).toHaveBeenCalledWith(tiendaId, dto);
  });

  it('should delete a tienda', async () => {
    service.delete.mockResolvedValue(undefined);

    await expect(controller.delete(tiendaId)).resolves.toBeUndefined();
    expect(service.delete).toHaveBeenCalledWith(tiendaId);
  });
});

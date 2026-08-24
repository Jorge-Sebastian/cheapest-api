import { EstadoCaptacion } from '../../repositories/entities';

export class TiendaResponseDto {
  id: string;
  codigoInterno: string;
  nombreComercial: string;
  responsableUsuarioId: string;
  rut: string;
  direccion: string;
  telefono: string;
  paisId: string;
  estadoCaptacion: EstadoCaptacion;
  createdAt: Date;
  updatedAt: Date;
}

import {
  IsEnum,
  IsOptional,
  IsString,
  IsUUID,
  MaxLength,
} from 'class-validator';
import { EstadoCaptacion } from '../../repositories/entities';

export class UpdateTiendaDto {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  codigoInterno?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  nombreComercial?: string;

  @IsOptional()
  @IsUUID()
  responsableUsuarioId?: string;

  @IsOptional()
  @IsString()
  @MaxLength(100)
  rut?: string;

  @IsOptional()
  @IsString()
  @MaxLength(255)
  direccion?: string;

  @IsOptional()
  @IsString()
  @MaxLength(30)
  telefono?: string;

  @IsOptional()
  @IsUUID()
  paisId?: string;

  @IsOptional()
  @IsEnum(EstadoCaptacion)
  estadoCaptacion?: EstadoCaptacion;
}

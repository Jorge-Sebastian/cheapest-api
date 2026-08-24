import {
  IsEnum,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsUUID,
  MaxLength,
} from 'class-validator';
import { EstadoCaptacion } from '../../repositories/entities';

export class CreateTiendaDto {
  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  codigoInterno: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  nombreComercial: string;

  @IsUUID()
  responsableUsuarioId: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(100)
  rut: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  direccion: string;

  @IsString()
  @IsNotEmpty()
  @MaxLength(30)
  telefono: string;

  @IsUUID()
  paisId: string;

  @IsOptional()
  @IsEnum(EstadoCaptacion)
  estadoCaptacion?: EstadoCaptacion;
}

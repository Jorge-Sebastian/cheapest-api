import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  ParseUUIDPipe,
  Patch,
  Post,
  ValidationPipe,
} from '@nestjs/common';
import { CreateTiendaDto, TiendaResponseDto, UpdateTiendaDto } from '../dtos';
import { TiendaService } from '../services';

@Controller('identification/tiendas')
export class TiendaController {
  constructor(private readonly tiendaService: TiendaService) {}

  @Post()
  create(
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: CreateTiendaDto,
  ): Promise<TiendaResponseDto> {
    return this.tiendaService.create(dto);
  }

  @Get()
  findAll(): Promise<TiendaResponseDto[]> {
    return this.tiendaService.findAll();
  }

  @Get(':id')
  findById(@Param('id', ParseUUIDPipe) id: string): Promise<TiendaResponseDto> {
    return this.tiendaService.findById(id);
  }

  @Patch(':id')
  update(
    @Param('id', ParseUUIDPipe) id: string,
    @Body(new ValidationPipe({ transform: true, whitelist: true }))
    dto: UpdateTiendaDto,
  ): Promise<TiendaResponseDto> {
    return this.tiendaService.update(id, dto);
  }

  @Delete(':id')
  delete(@Param('id', ParseUUIDPipe) id: string): Promise<void> {
    return this.tiendaService.delete(id);
  }
}

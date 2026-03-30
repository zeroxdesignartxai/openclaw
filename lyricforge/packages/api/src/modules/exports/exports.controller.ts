import { Body, Controller, Get, Post, BadRequestException } from '@nestjs/common';
import { ExportsService } from './exports.service';
import { projectSchema, Project } from '@lyricforge/shared';

@Controller('exports')
export class ExportsController {
  constructor(private readonly exportsService: ExportsService) {}

  @Get('health')
  health() {
    return { status: 'ok', service: 'exports' };
  }

  @Post()
  create(@Body() payload: unknown) {
    const parsed = projectSchema.safeParse(payload);
    if (!parsed.success) {
      throw new BadRequestException(parsed.error.format());
    }
    return this.exportsService.queueExport(parsed.data as Project);
  }
}

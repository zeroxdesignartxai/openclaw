import { Module } from '@nestjs/common';
import { ExportsController } from './modules/exports/exports.controller';
import { ExportsService } from './modules/exports/exports.service';

@Module({
  imports: [],
  controllers: [ExportsController],
  providers: [ExportsService]
})
export class AppModule {}

import { Controller, Get, Post, Body, Res } from '@nestjs/common';
import { Response } from 'express';
import { OfficerndService } from './officernd.service';
import { SyncStatusDto } from './dto/sync-status.dto';
import { SyncProgressDto } from './dto/sync-progress.dto';
import { SyncRunDto, SyncRunResponseDto } from './dto/sync-run.dto';

@Controller('api/officernd')
export class OfficerndController {
  constructor(private readonly officerndService: OfficerndService) {}

  @Get('status')
  async getStatus(): Promise<SyncStatusDto> {
    return this.officerndService.getStatus();
  }

  @Get('progress')
  async getProgress(): Promise<SyncProgressDto> {
    return this.officerndService.getProgress();
  }

  @Get('phases')
  async getPhases(): Promise<any> {
    return this.officerndService.getPhases();
  }

  @Get('companies')
  async getCompanyResults(): Promise<any[]> {
    return this.officerndService.getCompanyResults();
  }

  @Get('export')
  async exportDatabase(@Res() res: Response): Promise<void> {
    return this.officerndService.exportDatabase(res);
  }

  @Post('sync/run')
  async triggerSync(@Body() body: SyncRunDto): Promise<SyncRunResponseDto> {
    return this.officerndService.triggerSync(body);
  }
}

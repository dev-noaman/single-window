import { Injectable, Inject } from '@nestjs/common';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { HttpService } from '@nestjs/axios';
import { ConfigService } from '@nestjs/config';
import { Cache } from 'cache-manager';
import { SyncStatusDto } from './dto/sync-status.dto';
import { SyncProgressDto } from './dto/sync-progress.dto';
import { SyncRunDto, SyncRunResponseDto } from './dto/sync-run.dto';

@Injectable()
export class OfficerndService {
  private readonly apiUrl: string;
  private readonly orgSlug: string;

  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    private readonly httpService: HttpService,
    private readonly configService: ConfigService,
  ) {
    this.apiUrl = this.configService.get<string>('OFFICERND_API_URL') || 'http://localhost:8087';
    this.orgSlug = this.configService.get<string>('OFFICERND_ORG_SLUG') || 'arafat-business-centers';
  }

  async getStatus(): Promise<SyncStatusDto> {
    const cacheKey = 'officernd:status';
    const cached = await this.cacheManager.get<SyncStatusDto>(cacheKey);

    if (cached) {
      return cached;
    }

    try {
      // Call health, sync/status, and sync/stats endpoints in parallel
      const [healthResponse, syncStatusResponse, statsResponse] = await Promise.all([
        this.httpService.axiosRef.get(`${this.apiUrl}/health`),
        this.httpService.axiosRef.get(`${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/status`),
        this.httpService.axiosRef.get(`${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/stats`),
      ]);

      const healthData = healthResponse.data;
      const syncStatusData = syncStatusResponse.data;
      const statsData = statsResponse.data;

      // Extract last_sync from first record with last_run
      const lastSyncRecord = syncStatusData.find((record: any) => record.last_run);
      const last_sync = lastSyncRecord ? lastSyncRecord.last_run : 'Never';

      const result: SyncStatusDto = {
        success: true,
        api_status: 'online',
        companies: statsData.companies_total || 0,
        companies_active: statsData.companies_active || 0,
        companies_inactive: (statsData.companies_total || 0) - (statsData.companies_active || 0),
        companies_synced: statsData.companies_synced || 0,
        last_sync,
        health: healthData,
      };

      // Cache result with TTL 5000ms
      await this.cacheManager.set(cacheKey, result, 5000);

      return result;
    } catch (error: any) {
      return {
        success: false,
        api_status: 'offline',
        companies: 0,
        companies_active: 0,
        companies_inactive: 0,
        companies_synced: 0,
        last_sync: 'Never',
        message: error.code || error.message || 'API unreachable',
      };
    }
  }

  async getProgress(): Promise<SyncProgressDto> {
    const cacheKey = 'officernd:progress';
    const cached = await this.cacheManager.get<SyncProgressDto>(cacheKey);

    if (cached) {
      return cached;
    }

    try {
      const response = await this.httpService.axiosRef.get(
        `${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/progress`,
      );

      const result: SyncProgressDto = {
        status: response.data.status || 'idle',
        phase: response.data.phase || '',
        current: response.data.current || 0,
        total: response.data.total || 0,
        endpoint: response.data.endpoint || null,
        company: response.data.company || null,
        message: response.data.message || null,
        error: response.data.error || null,
        timestamp: response.data.timestamp || null,
      };

      // Cache result with TTL 1000ms for near-realtime progress
      await this.cacheManager.set(cacheKey, result, 1000);

      return result;
    } catch (error: any) {
      return {
        status: 'idle',
        phase: '',
        current: 0,
        total: 0,
        endpoint: null,
        company: null,
        message: 'No sync running',
        error: null,
        timestamp: null,
      };
    }
  }

  async getPhases(): Promise<any> {
    const cacheKey = 'officernd:phases';
    const cached = await this.cacheManager.get(cacheKey);
    if (cached) return cached;

    try {
      const response = await this.httpService.axiosRef.get(
        `${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/phases`,
      );
      await this.cacheManager.set(cacheKey, response.data, 2000);
      return response.data;
    } catch {
      return { current_phase: '', phases: [] };
    }
  }

  async getCompanyResults(): Promise<any[]> {
    try {
      const response = await this.httpService.axiosRef.get(
        `${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/companies`,
      );
      return response.data;
    } catch {
      return [];
    }
  }

  async exportDatabase(res: any): Promise<void> {
    try {
      const response = await this.httpService.axiosRef.get(
        `${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/export`,
        { responseType: 'stream' },
      );

      // Forward headers from FastAPI response
      const contentDisposition = response.headers['content-disposition'];
      if (contentDisposition) {
        res.setHeader('Content-Disposition', contentDisposition);
      }
      res.setHeader('Content-Type', 'application/octet-stream');

      // Pipe the stream
      response.data.pipe(res);
    } catch (error: any) {
      res.status(500).json({
        success: false,
        message: `Export failed: ${error.code || error.message || 'API unreachable'}`,
      });
    }
  }

  async triggerSync(body: SyncRunDto): Promise<SyncRunResponseDto> {
    const mode = body.mode || 'full';
    const resume = body.resume || false;

    try {
      const response = await this.httpService.axiosRef.post(
        `${this.apiUrl}/api/v2/organizations/${this.orgSlug}/sync/run`,
        { mode, resume },
      );

      if (response.data.status === 'already_running') {
        return {
          success: false,
          message: 'Sync already in progress',
        };
      }

      return {
        success: true,
        message: `${mode} sync started`,
        data: response.data,
      };
    } catch (error: any) {
      return {
        success: false,
        message: `Connection failed: ${error.code || error.message || 'API unreachable'}`,
      };
    }
  }
}

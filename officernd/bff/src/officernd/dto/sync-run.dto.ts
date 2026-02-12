export class SyncRunDto {
  mode?: 'full' | 'incremental' | 'smart';
  resume?: boolean;
}

export class SyncRunResponseDto {
  success: boolean;
  message: string;
  data?: any;
}

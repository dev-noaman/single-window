import { Module } from '@nestjs/common';
import { HttpModule } from '@nestjs/axios';
import { OfficerndService } from './officernd.service';
import { OfficerndController } from './officernd.controller';

@Module({
  imports: [
    HttpModule.register({
      timeout: 10000,
    }),
  ],
  providers: [OfficerndService],
  controllers: [OfficerndController],
})
export class OfficerndModule {}

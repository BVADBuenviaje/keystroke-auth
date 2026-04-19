import { Module } from '@nestjs/common';

import { AuthService } from './auth.service';
import { AuthController } from './auth.controller';
import { KeystrokeMathService } from './keystroke-math.service';
import { PrismaService } from './prisma.service';

@Module({
  providers: [AuthService, KeystrokeMathService, PrismaService],
  controllers: [AuthController]
})
export class AuthModule {}

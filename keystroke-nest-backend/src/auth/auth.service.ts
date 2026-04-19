import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PrismaService } from './prisma.service';
import { KeystrokeMathService } from './keystroke-math.service';
import { LoginBiometricDto } from './login-biometric.dto';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AuthService {
	constructor(
		private readonly prisma: PrismaService,
		private readonly math: KeystrokeMathService,
	) {}

	private readonly threshold = 2.5; // Tune as needed

	async validateUser(dto: LoginBiometricDto): Promise<{ success: boolean; reason?: string }> {
		const user = await this.prisma.user.findUnique({ where: { username: dto.username } });
		if (!user) throw new UnauthorizedException('Invalid credentials');

		const pwOk = await bcrypt.compare(dto.password, user.passwordHash);
		if (!pwOk) throw new UnauthorizedException('Invalid credentials');

		// Biometric anomaly detection
		const dwellScore = this.math.anomalyScore(dto.dwell, user.dwellMeans, user.dwellStddevs);
		const flightScore = this.math.anomalyScore(dto.flight, user.flightMeans, user.flightStddevs);
		const avgScore = (dwellScore + flightScore) / 2;

		if (avgScore > this.threshold) {
			return { success: false, reason: 'Biometric anomaly detected' };
		}
		return { success: true };
	}
}

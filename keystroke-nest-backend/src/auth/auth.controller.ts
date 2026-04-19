import { Controller, Post, Body } from '@nestjs/common';
import { AuthService } from './auth.service';
import { LoginBiometricDto } from './login-biometric.dto';

@Controller('auth')
export class AuthController {
	constructor(private readonly authService: AuthService) {}

	@Post('login')
	async login(@Body() dto: LoginBiometricDto) {
		return this.authService.validateUser(dto);
	}
}

import { IsString, IsObject, IsNotEmpty } from 'class-validator';

export class LoginBiometricDto {
  @IsString()
  @IsNotEmpty()
  username: string;

  @IsString()
  @IsNotEmpty()
  password: string;

  @IsObject()
  dwell: Record<string, number>;

  @IsObject()
  flight: Record<string, number>;
}

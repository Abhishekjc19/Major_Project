import { AppDataSource } from '../config/database';
import { User } from '../models/User';
import { authUtils } from '../utils/auth';

export class AuthService {
  private userRepository = AppDataSource.getRepository(User);

  async register(
    email: string,
    password: string,
    name: string,
    role: 'passenger' | 'conductor' | 'admin' = 'passenger'
  ): Promise<{ user: Partial<User>; token: string }> {
    // Check if user already exists
    const existingUser = await this.userRepository.findOne({ where: { email } });
    if (existingUser) {
      throw new Error('User with this email already exists');
    }

    // Hash password
    const password_hash = await authUtils.hashPassword(password);

    // Create user
    const user = this.userRepository.create({
      email,
      password_hash,
      name,
      role,
    });

    const savedUser = await this.userRepository.save(user);

    // Generate token
    const token = authUtils.generateToken(savedUser.id, savedUser.role);

    // Return user without password
    const { password_hash: _, ...userWithoutPassword } = savedUser;
    return { user: userWithoutPassword, token };
  }

  async login(email: string, password: string): Promise<{ user: Partial<User>; token: string }> {
    const user = await this.userRepository.findOne({ where: { email } });

    if (!user) {
      throw new Error('Invalid email or password');
    }

    // Compare password
    const isPasswordValid = await authUtils.comparePassword(password, user.password_hash);
    if (!isPasswordValid) {
      throw new Error('Invalid email or password');
    }

    if (!user.is_active) {
      throw new Error('User account is disabled');
    }

    // Generate token
    const token = authUtils.generateToken(user.id, user.role);

    // Return user without password
    const { password_hash: _, ...userWithoutPassword } = user;
    return { user: userWithoutPassword, token };
  }

  async getUserById(userId: string): Promise<Partial<User>> {
    const user = await this.userRepository.findOne({ where: { id: userId } });
    if (!user) {
      throw new Error('User not found');
    }

    const { password_hash: _, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }
}

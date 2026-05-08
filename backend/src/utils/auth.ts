import jwt from 'jwt-simple';
import bcrypt from 'bcryptjs';

const JWT_SECRET = process.env.JWT_SECRET || 'your_super_secret_key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

export const authUtils = {
  // Hash password
  hashPassword: async (password: string): Promise<string> => {
    const salt = await bcrypt.genSalt(10);
    return bcrypt.hash(password, salt);
  },

  // Compare password with hash
  comparePassword: async (password: string, hash: string): Promise<boolean> => {
    return bcrypt.compare(password, hash);
  },

  // Generate JWT token
  generateToken: (userId: string, role: string): string => {
    const payload = {
      userId,
      role,
      iat: Math.floor(Date.now() / 1000),
    };
    return jwt.encode(payload, JWT_SECRET, 'HS256');
  },

  // Verify JWT token
  verifyToken: (token: string): { userId: string; role: string } => {
    try {
      const decoded = jwt.decode(token, JWT_SECRET, true, 'HS256');
      return {
        userId: decoded.userId,
        role: decoded.role,
      };
    } catch (error) {
      throw new Error('Invalid token');
    }
  },

  // Extract token from Authorization header
  extractToken: (authHeader?: string): string | null => {
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return null;
    }
    return authHeader.slice(7);
  },
};

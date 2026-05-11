import bcrypt from 'bcryptjs';
import jwt from 'jwt-simple';

const JWT_SECRET = process.env.JWT_SECRET || 'your_super_secret_key';

export function normalizeEmail(email) {
  return String(email || '').trim().toLowerCase();
}

export function sanitizeUser(user) {
  if (!user) {
    return null;
  }

  const { password_hash, ...safeUser } = user;
  return safeUser;
}

export async function hashPassword(password) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

export function comparePassword(password, hash) {
  return bcrypt.compare(password, hash);
}

export function generateToken(user) {
  return jwt.encode(
    {
      userId: user.id,
      role: user.role,
      iat: Math.floor(Date.now() / 1000),
    },
    JWT_SECRET,
    'HS256',
  );
}

export function verifyToken(authHeader = '') {
  const token = authHeader.startsWith('Bearer ')
    ? authHeader.slice('Bearer '.length)
    : authHeader;

  if (!token) {
    throw new Error('Missing token');
  }

  return jwt.decode(token, JWT_SECRET, true, 'HS256');
}

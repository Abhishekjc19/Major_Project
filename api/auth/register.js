import { getBody, handleOptions, sendJson } from '../_lib/response.js';
import {
  generateToken,
  hashPassword,
  normalizeEmail,
  sanitizeUser,
} from '../_lib/auth.js';
import { createUser, findUserByEmail } from '../_lib/supabase.js';

const allowedRoles = new Set(['passenger', 'conductor', 'admin']);

export default async function handler(req, res) {
  if (handleOptions(req, res)) return;

  if (req.method !== 'POST') {
    return sendJson(req, res, 405, { error: 'Method not allowed' });
  }

  try {
    const body = getBody(req);
    const { password } = body;
    const email = normalizeEmail(body.email);
    const name = String(body.name || '').trim();
    const role = allowedRoles.has(body.role)
      ? body.role
      : 'passenger';

    if (!email || !password || !name) {
      return sendJson(req, res, 400, { error: 'Missing required fields' });
    }

    const existingUser = await findUserByEmail(email);
    if (existingUser) {
      return sendJson(req, res, 400, {
        error: 'User with this email already exists',
      });
    }

    const user = await createUser({
      email,
      password_hash: await hashPassword(password),
      name,
      role,
      is_active: true,
    });

    return sendJson(req, res, 201, {
      user: sanitizeUser(user),
      token: generateToken(user),
    });
  } catch (error) {
    console.error('Register failed:', error);
    return sendJson(req, res, error.status || 500, {
      error: error.status ? error.message : 'Unable to create account',
    });
  }
}

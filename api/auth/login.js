import { getBody, handleOptions, sendJson } from '../_lib/response.js';
import {
  comparePassword,
  generateToken,
  normalizeEmail,
  sanitizeUser,
} from '../_lib/auth.js';
import { findUserByEmail } from '../_lib/supabase.js';

export default async function handler(req, res) {
  if (handleOptions(req, res)) return;

  if (req.method !== 'POST') {
    return sendJson(req, res, 405, { error: 'Method not allowed' });
  }

  try {
    const body = getBody(req);
    const { password } = body;
    const email = normalizeEmail(body.email);

    if (!email || !password) {
      return sendJson(req, res, 400, { error: 'Email and password required' });
    }

    const user = await findUserByEmail(email);
    const passwordMatches = user
      ? await comparePassword(password, user.password_hash)
      : false;

    if (!user || !passwordMatches) {
      return sendJson(req, res, 401, { error: 'Invalid email or password' });
    }

    if (user.is_active === false) {
      return sendJson(req, res, 401, { error: 'User account is disabled' });
    }

    return sendJson(req, res, 200, {
      user: sanitizeUser(user),
      token: generateToken(user),
    });
  } catch (error) {
    console.error('Login failed:', error);
    return sendJson(req, res, error.status || 500, {
      error: error.status ? error.message : 'Unable to sign in',
    });
  }
}

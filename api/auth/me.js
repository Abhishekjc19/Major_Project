import { handleOptions, sendJson } from '../_lib/response.js';
import { sanitizeUser, verifyToken } from '../_lib/auth.js';
import { findUserById } from '../_lib/supabase.js';

export default async function handler(req, res) {
  if (handleOptions(req, res)) return;

  if (req.method !== 'GET') {
    return sendJson(req, res, 405, { error: 'Method not allowed' });
  }

  try {
    const decoded = verifyToken(req.headers.authorization || '');
    const user = await findUserById(decoded.userId);

    if (!user) {
      return sendJson(req, res, 404, { error: 'User not found' });
    }

    return sendJson(req, res, 200, sanitizeUser(user));
  } catch {
    return sendJson(req, res, 401, { error: 'Unauthorized' });
  }
}

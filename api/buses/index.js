import { handleOptions, sendJson } from '../_lib/response.js';
import { listBuses } from '../_lib/supabase.js';

export default async function handler(req, res) {
  if (handleOptions(req, res)) return;

  if (req.method !== 'GET') {
    return sendJson(req, res, 405, { error: 'Method not allowed' });
  }

  try {
    const buses = await listBuses();
    return sendJson(req, res, 200, buses);
  } catch (error) {
    console.error('Buses request failed:', error);
    return sendJson(req, res, error.status || 500, {
      error: error.status ? error.message : 'Unable to load buses',
    });
  }
}

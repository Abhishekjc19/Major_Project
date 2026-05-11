import { handleOptions, sendJson } from './_lib/response.js';

export default function handler(req, res) {
  if (handleOptions(req, res)) return;

  return sendJson(req, res, 200, {
    status: 'ok',
    timestamp: new Date().toISOString(),
  });
}

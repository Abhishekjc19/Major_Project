export function setCors(req, res) {
  const origin = req.headers.origin || '*';
  res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
}

export function sendJson(req, res, status, payload) {
  setCors(req, res);
  res.status(status).json(payload);
}

export function handleOptions(req, res) {
  if (req.method !== 'OPTIONS') {
    return false;
  }

  setCors(req, res);
  res.status(204).end();
  return true;
}

export function getBody(req) {
  if (!req.body) {
    return {};
  }

  if (typeof req.body === 'string') {
    try {
      return JSON.parse(req.body);
    } catch {
      return {};
    }
  }

  return req.body;
}

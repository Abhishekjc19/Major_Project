import { VercelRequest, VercelResponse } from '@vercel/node';
import app from './app';

export default (req: VercelRequest, res: VercelResponse) => {
  return app(req, res);
};

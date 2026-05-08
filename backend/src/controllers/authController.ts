import { Response } from 'express';
import { AuthRequest } from '../middleware/auth';
import { AuthService } from '../services/AuthService';

const authService = new AuthService();

export const authController = {
  register: async (req: AuthRequest, res: Response) => {
    try {
      const { email, password, name, role } = req.body;

      if (!email || !password || !name) {
        return res.status(400).json({ error: 'Missing required fields' });
      }

      const result = await authService.register(email, password, name, role);
      res.status(201).json(result);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  },

  login: async (req: AuthRequest, res: Response) => {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({ error: 'Email and password required' });
      }

      const result = await authService.login(email, password);
      res.status(200).json(result);
    } catch (error: any) {
      res.status(401).json({ error: error.message });
    }
  },

  getMe: async (req: AuthRequest, res: Response) => {
    try {
      if (!req.userId) {
        return res.status(401).json({ error: 'Unauthorized' });
      }

      const user = await authService.getUserById(req.userId);
      res.status(200).json(user);
    } catch (error: any) {
      res.status(404).json({ error: error.message });
    }
  },
};

import { Request, Response, NextFunction } from 'express';
import { authUtils } from '../utils/auth';

export interface AuthRequest extends Request {
  userId?: string;
  userRole?: string;
}

// Authentication middleware
export const authMiddleware = (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const token = authUtils.extractToken(req.headers.authorization);

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = authUtils.verifyToken(token);
    req.userId = decoded.userId;
    req.userRole = decoded.role;

    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};

// Role-based authorization middleware
export const requireRole = (...roles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.userRole || !roles.includes(req.userRole)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

// Error handling middleware
export const errorHandler = (
  err: any,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error('Error:', err);

  const status = err.status || 500;
  const message = err.message || 'Internal server error';

  res.status(status).json({
    error: message,
    status,
  });
};

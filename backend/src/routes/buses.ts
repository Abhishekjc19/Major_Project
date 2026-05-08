import { Router } from 'express';
import { busController } from '../controllers/busController';
import { authMiddleware, requireRole } from '../middleware/auth';

const router = Router();

// Public routes (accessible to all authenticated users)
router.get('/', authMiddleware, busController.getAllBuses);
router.get('/:id', authMiddleware, busController.getBusById);

// Conductor-only routes
router.post(
  '/:id/occupancy',
  authMiddleware,
  requireRole('conductor', 'admin'),
  busController.updateOccupancy
);

router.post(
  '/:id/location',
  authMiddleware,
  requireRole('conductor', 'admin'),
  busController.updateLocation
);

router.post(
  '/:busId/stops/:stopId/mark-passed',
  authMiddleware,
  requireRole('conductor', 'admin'),
  busController.markStopAsPassed
);

export default router;

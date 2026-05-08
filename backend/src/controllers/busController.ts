import { Response } from 'express';
import { AuthRequest } from '../middleware/auth';
import { BusService } from '../services/BusService';

const busService = new BusService();

export const busController = {
  getAllBuses: async (req: AuthRequest, res: Response) => {
    try {
      const { status, route } = req.query;
      const buses = await busService.getAllBuses({
        status: status as string,
        route: route as string,
      });
      res.status(200).json(buses);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  },

  getBusById: async (req: AuthRequest, res: Response) => {
    try {
      const { id } = req.params;
      const bus = await busService.getBusById(id);
      res.status(200).json(bus);
    } catch (error: any) {
      res.status(404).json({ error: error.message });
    }
  },

  updateOccupancy: async (req: AuthRequest, res: Response) => {
    try {
      if (req.userRole !== 'conductor' && req.userRole !== 'admin') {
        return res.status(403).json({ error: 'Only conductors can update occupancy' });
      }

      const { id } = req.params;
      const { change } = req.body;

      if (typeof change !== 'number') {
        return res.status(400).json({ error: 'Change must be a number' });
      }

      const bus = await busService.updateBusOccupancy(id, change);
      res.status(200).json(bus);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  },

  updateLocation: async (req: AuthRequest, res: Response) => {
    try {
      if (req.userRole !== 'conductor' && req.userRole !== 'admin') {
        return res.status(403).json({ error: 'Only conductors can update location' });
      }

      const { id } = req.params;
      const { latitude, longitude } = req.body;

      if (typeof latitude !== 'number' || typeof longitude !== 'number') {
        return res.status(400).json({ error: 'Invalid coordinates' });
      }

      const bus = await busService.updateBusLocation(id, latitude, longitude);
      res.status(200).json(bus);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  },

  markStopAsPassed: async (req: AuthRequest, res: Response) => {
    try {
      if (req.userRole !== 'conductor' && req.userRole !== 'admin') {
        return res.status(403).json({ error: 'Only conductors can mark stops' });
      }

      const { busId, stopId } = req.params;
      const routeStop = await busService.markStopAsPassed(busId, stopId);
      res.status(200).json(routeStop);
    } catch (error: any) {
      res.status(500).json({ error: error.message });
    }
  },
};

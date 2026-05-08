import { Socket, Server as SocketIOServer } from 'socket.io';
import { BusService } from '../services/BusService';
import { AppDataSource } from '../config/database';
import { LostItem } from '../models/LostItem';
import { ChatMessage } from '../models/ChatMessage';

const busService = new BusService();

export function setupSocketHandlers(socket: Socket, io: SocketIOServer) {
  const userId = socket.data.userId;
  const userRole = socket.data.userRole;

  // Join user-specific room
  socket.join(`user:${userId}`);

  // Join conductor room if conductor
  if (userRole === 'conductor') {
    socket.join('conductors');
  }

  // Request initial buses data
  socket.on('buses:request-update', async () => {
    try {
      console.log(`[${socket.id}] Received buses:request-update`);
      const buses = await busService.getAllBuses();
      console.log(`[${socket.id}] Fetched ${buses.length} buses, sending to client`);
      socket.emit('buses:init', buses);
    } catch (error) {
      console.error(`[${socket.id}] Error fetching buses:`, error);
      socket.emit('error', { message: 'Failed to fetch buses' });
    }
  });

  // Conductor: Update occupancy
  socket.on('ticket:sold', async (data: { busId: string; count: number }) => {
    try {
      if (userRole !== 'conductor' && userRole !== 'admin') {
        socket.emit('error', { message: 'Unauthorized' });
        return;
      }

      const bus = await busService.updateBusOccupancy(data.busId, data.count);

      // Broadcast update to all clients
      io.emit('bus:update', bus);
      console.log(`Ticket sold: Bus ${bus.route_number}, New occupancy: ${bus.current_occupancy}`);
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // Conductor: Cancel ticket
  socket.on('ticket:cancelled', async (data: { busId: string; count: number }) => {
    try {
      if (userRole !== 'conductor' && userRole !== 'admin') {
        socket.emit('error', { message: 'Unauthorized' });
        return;
      }

      const bus = await busService.updateBusOccupancy(data.busId, -data.count);

      // Broadcast update to all clients
      io.emit('bus:update', bus);
      console.log(`Ticket cancelled: Bus ${bus.route_number}, New occupancy: ${bus.current_occupancy}`);
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // Conductor: Update bus location
  socket.on('bus:location-update', async (data: { busId: string; latitude: number; longitude: number }) => {
    try {
      if (userRole !== 'conductor' && userRole !== 'admin') {
        socket.emit('error', { message: 'Unauthorized' });
        return;
      }

      const bus = await busService.updateBusLocation(data.busId, data.latitude, data.longitude);
      io.emit('bus:update', bus);
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // Conductor: Mark stop as passed
  socket.on('bus:stop-passed', async (data: { busId: string; stopId: string }) => {
    try {
      if (userRole !== 'conductor' && userRole !== 'admin') {
        socket.emit('error', { message: 'Unauthorized' });
        return;
      }

      await busService.markStopAsPassed(data.busId, data.stopId);

      // Emit event to all connected clients
      io.emit('bus:stop-reached', {
        busId: data.busId,
        stopId: data.stopId,
        timestamp: new Date(),
      });
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // Chat: Send message in lost & found
  socket.on('chat:message', async (data: { lostItemId: string; message: string }) => {
    try {
      const lostItemRepository = AppDataSource.getRepository(LostItem);
      const chatRepository = AppDataSource.getRepository(ChatMessage);

      // Verify lost item exists
      const lostItem = await lostItemRepository.findOne({
        where: { id: data.lostItemId },
      });

      if (!lostItem) {
        socket.emit('error', { message: 'Lost item not found' });
        return;
      }

      // Create chat message
      const chatMessage = chatRepository.create({
        lost_item_id: data.lostItemId,
        sender_id: userId,
        message_text: data.message,
      });

      const savedMessage = await chatRepository.save(chatMessage);

      // Broadcast to relevant parties
      io.to(`user:${lostItem.user_id}`).emit('chat:message', {
        lostItemId: data.lostItemId,
        message: savedMessage.message_text,
        senderId: userId,
        senderRole: userRole,
        timestamp: savedMessage.created_at,
      });

      // Also notify conductors
      if (userRole === 'passenger') {
        io.to('conductors').emit('chat:message', {
          lostItemId: data.lostItemId,
          message: savedMessage.message_text,
          senderId: userId,
          senderRole: userRole,
          timestamp: savedMessage.created_at,
        });
      }
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // SOS: Emergency alert
  socket.on('sos:activate', async (data?: { description?: string; busId?: string }) => {
    try {
      const SOSAlert = require('../models/SOSAlert').SOSAlert;
      const sosRepository = AppDataSource.getRepository(SOSAlert);

      const sosAlert = sosRepository.create({
        user_id: userId,
        bus_id: data?.busId,
        description: data?.description,
        status: 'active',
      });

      const savedAlert = await sosRepository.save(sosAlert);

      // Broadcast SOS alert to admins and conductors
      io.to('conductors').emit('sos:alert', {
        sosId: savedAlert.id,
        userId,
        timestamp: savedAlert.created_at,
        description: savedAlert.description,
        busId: savedAlert.bus_id,
      });

      socket.emit('sos:activated', { sosId: savedAlert.id });
      console.log(`SOS Alert activated by user: ${userId}`);
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });

  // Conductor: Update SOS status
  socket.on('sos:update-status', async (data: { sosId: string; status: 'active' | 'responding' | 'resolved' }) => {
    try {
      if (userRole !== 'conductor' && userRole !== 'admin') {
        socket.emit('error', { message: 'Unauthorized' });
        return;
      }

      const SOSAlert = require('../models/SOSAlert').SOSAlert;
      const sosRepository = AppDataSource.getRepository(SOSAlert);

      const sos = await sosRepository.findOne({ where: { id: data.sosId } });
      if (!sos) {
        socket.emit('error', { message: 'SOS alert not found' });
        return;
      }

      sos.status = data.status;
      if (data.status === 'resolved') {
        sos.resolved_at = new Date();
      }

      await sosRepository.save(sos);

      // Broadcast update
      io.emit('sos:status-updated', {
        sosId: sos.id,
        status: sos.status,
      });
    } catch (error: any) {
      socket.emit('error', { message: error.message });
    }
  });
}

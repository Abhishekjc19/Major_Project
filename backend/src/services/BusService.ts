import { AppDataSource } from '../config/database';
import { Bus } from '../models/Bus';
import { RouteStop } from '../models/RouteStop';
import { BusStop } from '../models/BusStop';

export class BusService {
  private busRepository = AppDataSource.getRepository(Bus);
  private routeStopRepository = AppDataSource.getRepository(RouteStop);

  async getAllBuses(filters?: { status?: string; route?: string }): Promise<Bus[]> {
    let query = this.busRepository.createQueryBuilder('bus')
      .leftJoinAndSelect('bus.stops', 'stops')
      .leftJoinAndSelect('stops.stop', 'stop')
      .orderBy('stops.sequence_order', 'ASC');

    if (filters?.status) {
      query = query.where('bus.status = :status', { status: filters.status });
    }

    if (filters?.route) {
      query = query.andWhere('bus.route_number ILIKE :route', { route: `%${filters.route}%` });
    }

    return query.getMany();
  }

  async getBusById(busId: string): Promise<Bus> {
    const bus = await this.busRepository.findOne({
      where: { id: busId },
      relations: ['stops', 'stops.stop', 'assigned_conductor'],
    });

    if (!bus) {
      throw new Error('Bus not found');
    }

    return bus;
  }

  async updateBusOccupancy(busId: string, change: number): Promise<Bus> {
    const bus = await this.getBusById(busId);

    bus.current_occupancy = Math.max(0, Math.min(bus.capacity, bus.current_occupancy + change));
    bus.updateStatus();
    bus.last_updated = 'Just now';

    return this.busRepository.save(bus);
  }

  async updateBusLocation(busId: string, latitude: number, longitude: number): Promise<Bus> {
    const bus = await this.getBusById(busId);

    bus.current_location_lat = latitude;
    bus.current_location_lon = longitude;
    bus.last_updated = 'Just now';

    return this.busRepository.save(bus);
  }

  async markStopAsPassed(busId: string, stopId: string): Promise<RouteStop> {
    const routeStop = await this.routeStopRepository.findOne({
      where: { bus_id: busId, stop_id: stopId },
      relations: ['bus', 'stop'],
    });

    if (!routeStop) {
      throw new Error('Stop not found for this bus');
    }

    routeStop.is_passed = true;

    return this.routeStopRepository.save(routeStop);
  }

  async createBus(data: {
    route_number: string;
    destination: string;
    capacity: number;
    stops: Array<{ stop_id: string; estimated_arrival_time: string }>;
  }): Promise<Bus> {
    const bus = this.busRepository.create({
      route_number: data.route_number,
      destination: data.destination,
      capacity: data.capacity,
      current_occupancy: 0,
      status: 'available',
    });

    const savedBus = await this.busRepository.save(bus);

    // Create route stops
    for (let i = 0; i < data.stops.length; i++) {
      const routeStop = this.routeStopRepository.create({
        bus_id: savedBus.id,
        stop_id: data.stops[i].stop_id,
        sequence_order: i,
        estimated_arrival_time: data.stops[i].estimated_arrival_time,
        is_passed: false,
      });
      await this.routeStopRepository.save(routeStop);
    }

    return this.getBusById(savedBus.id);
  }
}

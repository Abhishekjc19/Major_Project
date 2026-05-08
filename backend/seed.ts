import 'reflect-metadata';
import { AppDataSource } from './src/config/database';
import { User } from './src/models/User';
import { Bus } from './src/models/Bus';
import { BusStop } from './src/models/BusStop';
import { RouteStop } from './src/models/RouteStop';
import { authUtils } from './src/utils/auth';

async function seedDatabase() {
  try {
    console.log('Initializing database connection...');
    await AppDataSource.initialize();
    console.log('Database connected');

    // Create repositories
    const userRepo = AppDataSource.getRepository(User);
    const busRepo = AppDataSource.getRepository(Bus);
    const stopRepo = AppDataSource.getRepository(BusStop);
    const routeStopRepo = AppDataSource.getRepository(RouteStop);

    // Clear existing data
    console.log('Clearing existing data...');
    try {
      await routeStopRepo.clear();
      await busRepo.clear();
      await stopRepo.clear();
      await userRepo.clear();
    } catch (e) {
      console.log('(No existing data to clear)');
    }

    // Create demo users
    console.log('Creating demo users...');
    const passengerPassword = await authUtils.hashPassword('demo123');
    const conductorPassword = await authUtils.hashPassword('demo123');

    const passenger = userRepo.create({
      email: 'passenger@demo.com',
      password_hash: passengerPassword,
      name: 'Demo Passenger',
      role: 'passenger',
    });

    const conductor = userRepo.create({
      email: 'conductor@demo.com',
      password_hash: conductorPassword,
      name: 'Demo Conductor',
      role: 'conductor',
    });

    const admin = userRepo.create({
      email: 'admin@demo.com',
      password_hash: conductorPassword,
      name: 'Admin User',
      role: 'admin',
    });

    await userRepo.save([passenger, conductor, admin]);
    console.log('✓ Demo users created');

    // Create bus stops
    console.log('Creating bus stops...');
    const stops = stopRepo.create([
      {
        name: 'Pine Avenue',
        latitude: 40.7128,
        longitude: -74.006,
        street_address: '123 Pine Ave',
      },
      {
        name: 'Oak Street',
        latitude: 40.758,
        longitude: -73.9855,
        street_address: '456 Oak St',
      },
      {
        name: 'Maple Road',
        latitude: 40.7614,
        longitude: -73.9776,
        street_address: '789 Maple Rd',
      },
      {
        name: 'Central Station',
        latitude: 40.7489,
        longitude: -73.9680,
        street_address: '100 Central Ave',
      },
      {
        name: 'West Gate',
        latitude: 40.7505,
        longitude: -73.9972,
        street_address: '200 West Gate',
      },
      {
        name: 'Market Square',
        latitude: 40.7549,
        longitude: -73.9840,
        street_address: '300 Market St',
      },
      {
        name: 'Harbor View',
        latitude: 40.7061,
        longitude: -74.0088,
        street_address: '400 Harbor Ln',
      },
      {
        name: 'City Center',
        latitude: 40.7549,
        longitude: -73.9840,
        street_address: '500 City Center Pl',
      },
      {
        name: 'Innovation Way',
        latitude: 40.7689,
        longitude: -73.9830,
        street_address: '600 Innovation Way',
      },
      {
        name: 'Tech Park',
        latitude: 40.7282,
        longitude: -73.7949,
        street_address: '700 Tech Park Dr',
      },
    ]);

    const savedStops = await stopRepo.save(stops);
    console.log('✓ Bus stops created');

    // Create buses with stops
    console.log('Creating buses...');
    const buses = [
      {
        route_number: '42A',
        destination: 'Central Station',
        capacity: 50,
        stopIndices: [0, 1, 2, 3],
      },
      {
        route_number: '15C',
        destination: 'North Harbor',
        capacity: 50,
        stopIndices: [4, 5, 6],
      },
      {
        route_number: '88',
        destination: 'Tech Park',
        capacity: 50,
        stopIndices: [7, 8, 9],
      },
    ];

    for (const busData of buses) {
      const bus = busRepo.create({
        route_number: busData.route_number,
        destination: busData.destination,
        capacity: busData.capacity,
        current_occupancy: Math.floor(Math.random() * (busData.capacity * 0.9)),
        assigned_conductor: conductor,
      });

      const savedBus = await busRepo.save(bus);

      // Create route stops
      for (let i = 0; i < busData.stopIndices.length; i++) {
        const routeStop = routeStopRepo.create({
          bus: savedBus,
          stop: savedStops[busData.stopIndices[i]],
          sequence_order: i,
          estimated_arrival_time: `${10 + i * 8}:${i * 7}0`,
          is_passed: i === 0,
        });
        await routeStopRepo.save(routeStop);
      }

      // Update status based on occupancy
      savedBus.updateStatus();
      await busRepo.save(savedBus);
    }

    console.log('✓ Buses and routes created');

    console.log('\n✅ Database seeded successfully!');
    console.log('\nDemo Credentials:');
    console.log('Passenger: passenger@demo.com / demo123');
    console.log('Conductor: conductor@demo.com / demo123');
    console.log('Admin: admin@demo.com / demo123');

    await AppDataSource.destroy();
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

seedDatabase();

import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  OneToMany,
  CreateDateColumn,
} from 'typeorm';
import { RouteStop } from './RouteStop';

@Entity('bus_stops')
export class BusStop {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar' })
  name: string;

  @Column({ type: 'decimal', precision: 10, scale: 8 })
  latitude: number;

  @Column({ type: 'decimal', precision: 11, scale: 8 })
  longitude: number;

  @Column({ type: 'varchar', nullable: true })
  street_address?: string;

  @CreateDateColumn()
  created_at: Date;

  // Relations
  @OneToMany(() => RouteStop, (routeStop) => routeStop.stop)
  route_stops: RouteStop[];
}

import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  JoinColumn,
  CreateDateColumn,
} from 'typeorm';
import { Bus } from './Bus';
import { BusStop } from './BusStop';

@Entity('route_stops')
export class RouteStop {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'integer' })
  sequence_order: number;

  @Column({ type: 'time', nullable: true })
  estimated_arrival_time?: string;

  @Column({ type: 'boolean', default: false })
  is_passed: boolean;

  @ManyToOne(() => Bus, (bus) => bus.stops, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'bus_id' })
  bus: Bus;

  @Column({ type: 'varchar' })
  bus_id: string;

  @ManyToOne(() => BusStop, (stop) => stop.route_stops)
  @JoinColumn({ name: 'stop_id' })
  stop: BusStop;

  @Column({ type: 'varchar' })
  stop_id: string;

  @CreateDateColumn()
  created_at: Date;
}

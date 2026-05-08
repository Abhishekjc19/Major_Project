import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  JoinColumn,
  CreateDateColumn,
} from 'typeorm';
import { User } from './User';
import { Bus } from './Bus';
import { BusStop } from './BusStop';

@Entity('ride_history')
export class RideHistory {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'date' })
  ride_date: Date;

  @Column({ type: 'decimal', precision: 10, scale: 2 })
  fare: number;

  @ManyToOne(() => User, (user) => user.ride_history, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ type: 'varchar' })
  user_id: string;

  @ManyToOne(() => Bus, (bus) => bus.rides, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'bus_id' })
  bus: Bus;

  @Column({ type: 'varchar', nullable: true })
  bus_id: string;

  @ManyToOne(() => BusStop, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'from_stop_id' })
  from_stop: BusStop;

  @Column({ type: 'varchar', nullable: true })
  from_stop_id: string;

  @ManyToOne(() => BusStop, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'to_stop_id' })
  to_stop: BusStop;

  @Column({ type: 'varchar', nullable: true })
  to_stop_id: string;

  @CreateDateColumn()
  created_at: Date;
}

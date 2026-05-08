import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  ManyToOne,
  OneToMany,
  JoinColumn,
} from 'typeorm';
import { User } from './User';
import { RouteStop } from './RouteStop';
import { RideHistory } from './RideHistory';
import { LostItem } from './LostItem';

export type OccupancyStatus = 'available' | 'partial' | 'full';

@Entity('buses')
export class Bus {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true, type: 'varchar' })
  route_number: string;

  @Column({ type: 'varchar' })
  destination: string;

  @Column({ type: 'integer' })
  capacity: number;

  @Column({ type: 'integer', default: 0 })
  current_occupancy: number;

  @Column({ type: 'varchar', default: 'available' })
  status: OccupancyStatus;

  @Column({ type: 'decimal', precision: 10, scale: 8, nullable: true })
  current_location_lat: number;

  @Column({ type: 'decimal', precision: 11, scale: 8, nullable: true })
  current_location_lon: number;

  @Column({ type: 'varchar', default: 'Just now' })
  last_updated: string;

  @ManyToOne(() => User, (user) => user.assigned_buses, { nullable: true })
  @JoinColumn({ name: 'assigned_conductor_id' })
  assigned_conductor: User;

  @Column({ type: 'varchar', nullable: true })
  assigned_conductor_id: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  // Relations
  @OneToMany(() => RouteStop, (routeStop) => routeStop.bus)
  stops: RouteStop[];

  @OneToMany(() => RideHistory, (ride) => ride.bus)
  rides: RideHistory[];

  @OneToMany(() => LostItem, (item) => item.bus)
  lost_items: LostItem[];

  // Helper method to calculate occupancy percentage
  getOccupancyPercentage(): number {
    return Math.round((this.current_occupancy / this.capacity) * 100);
  }

  // Helper method to update status based on occupancy
  updateStatus(): void {
    const ratio = this.current_occupancy / this.capacity;
    if (ratio < 0.5) {
      this.status = 'available';
    } else if (ratio < 0.9) {
      this.status = 'partial';
    } else {
      this.status = 'full';
    }
  }
}

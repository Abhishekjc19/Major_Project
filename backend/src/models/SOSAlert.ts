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

export type SOSStatus = 'active' | 'responding' | 'resolved';

@Entity('sos_alerts')
export class SOSAlert {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar', default: 'active' })
  status: SOSStatus;

  @Column({ type: 'text', nullable: true })
  description?: string;

  @ManyToOne(() => User, (user) => user.sos_alerts, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ type: 'varchar' })
  user_id: string;

  @ManyToOne(() => Bus, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'bus_id' })
  bus: Bus;

  @Column({ type: 'varchar', nullable: true })
  bus_id: string;

  @CreateDateColumn()
  created_at: Date;

  @Column({ type: 'timestamp', nullable: true })
  resolved_at: Date;
}

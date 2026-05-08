import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  OneToMany,
} from 'typeorm';
import { Bus } from './Bus';
import { RideHistory } from './RideHistory';
import { LostItem } from './LostItem';
import { ChatMessage } from './ChatMessage';
import { SOSAlert } from './SOSAlert';

export type UserRole = 'passenger' | 'conductor' | 'admin';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true, type: 'varchar' })
  email: string;

  @Column({ type: 'varchar' })
  password_hash: string;

  @Column({ type: 'varchar' })
  name: string;

  @Column({ type: 'varchar', default: 'passenger' })
  role: UserRole;

  @Column({ type: 'varchar', nullable: true })
  phone?: string;

  @Column({ type: 'boolean', default: true })
  is_active: boolean;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  // Relations
  @OneToMany(() => Bus, (bus) => bus.assigned_conductor)
  assigned_buses: Bus[];

  @OneToMany(() => RideHistory, (ride) => ride.user)
  ride_history: RideHistory[];

  @OneToMany(() => LostItem, (item) => item.user)
  lost_items: LostItem[];

  @OneToMany(() => ChatMessage, (msg) => msg.sender)
  chat_messages: ChatMessage[];

  @OneToMany(() => SOSAlert, (sos) => sos.user)
  sos_alerts: SOSAlert[];
}

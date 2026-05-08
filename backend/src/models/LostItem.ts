import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  OneToMany,
  JoinColumn,
  CreateDateColumn,
  UpdateDateColumn,
} from 'typeorm';
import { User } from './User';
import { Bus } from './Bus';
import { ChatMessage } from './ChatMessage';

export type LostItemStatus = 'searching' | 'found' | 'returned';

@Entity('lost_items')
export class LostItem {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'varchar' })
  item_name: string;

  @Column({ type: 'varchar' })
  description: string;

  @Column({ type: 'varchar', default: 'searching' })
  status: LostItemStatus;

  @Column({ type: 'date' })
  reported_date: Date;

  @ManyToOne(() => User, (user) => user.lost_items, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'user_id' })
  user: User;

  @Column({ type: 'varchar' })
  user_id: string;

  @ManyToOne(() => Bus, (bus) => bus.lost_items, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'bus_id' })
  bus: Bus;

  @Column({ type: 'varchar', nullable: true })
  bus_id: string;

  @CreateDateColumn()
  created_at: Date;

  @UpdateDateColumn()
  updated_at: Date;

  // Relations
  @OneToMany(() => ChatMessage, (msg) => msg.lost_item)
  chat_messages: ChatMessage[];
}

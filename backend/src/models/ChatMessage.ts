import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  JoinColumn,
  CreateDateColumn,
} from 'typeorm';
import { User } from './User';
import { LostItem } from './LostItem';

@Entity('chat_messages')
export class ChatMessage {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ type: 'text' })
  message_text: string;

  @ManyToOne(() => LostItem, (item) => item.chat_messages, { onDelete: 'CASCADE' })
  @JoinColumn({ name: 'lost_item_id' })
  lost_item: LostItem;

  @Column({ type: 'varchar' })
  lost_item_id: string;

  @ManyToOne(() => User, (user) => user.chat_messages, { onDelete: 'SET NULL', nullable: true })
  @JoinColumn({ name: 'sender_id' })
  sender: User;

  @Column({ type: 'varchar', nullable: true })
  sender_id: string;

  @CreateDateColumn()
  created_at: Date;
}

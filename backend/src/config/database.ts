import { DataSource } from 'typeorm';
import { config } from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const isProduction = process.env.NODE_ENV === 'production';
const isSqlite = process.env.DATABASE_TYPE === 'sqlite';

export const AppDataSource = new DataSource(
  isSqlite
    ? {
        type: 'sqlite',
        database: path.join(process.cwd(), 'omnibus.db'),
        synchronize: true,
        logging: false,
        entities: [path.join(__dirname, '../models/*.{ts,js}')],
        migrations: [path.join(__dirname, '../../migrations/*.{ts,js}')],
        subscribers: [],
      }
    : {
        type: 'postgres',
        host: process.env.DATABASE_HOST || 'localhost',
        port: parseInt(process.env.DATABASE_PORT || '5432'),
        username: process.env.DATABASE_USER || 'postgres',
        password: process.env.DATABASE_PASSWORD || 'postgres',
        database: process.env.DATABASE_NAME || 'omnibus',
        synchronize: process.env.NODE_ENV === 'development',
        logging: process.env.NODE_ENV === 'development',
        entities: [path.join(__dirname, '../models/*.{ts,js}')],
        migrations: [path.join(__dirname, '../../migrations/*.{ts,js}')],
        subscribers: [],
        ssl: process.env.DATABASE_SSL === 'true' ? { rejectUnauthorized: false } : false,
      }
);

import { Pool } from 'pg';
import { config } from './config';
import { logger } from './logger';

export const pool = new Pool({
  connectionString: config.DATABASE_URL,
});

pool.on('error', (err) => {
  logger.error(err, 'Unexpected error on idle pg client');
});

export const query = (text: string, params?: any[]) => pool.query(text, params);

export const initSchema = async () => {
  await query(`
    CREATE TABLE IF NOT EXISTS tickets (
      id UUID PRIMARY KEY,
      user_id TEXT NOT NULL,
      original_text TEXT NOT NULL,
      detected_language TEXT,
      translated_text TEXT,
      ai_response TEXT,
      audio_url TEXT,
      status TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
  `);
  logger.info('Database schema initialized');
};

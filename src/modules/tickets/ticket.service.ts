import { CreateTicketDTO, Ticket, TicketStatus } from './ticket.schema';
import { randomUUID } from 'crypto';
import { logger } from '../../core/logger';
import { query } from '../../core/database';

export class TicketService {
  constructor(private readonly jobQueue: any) { }

  async createTicket(userId: string, data: CreateTicketDTO): Promise<Ticket> {
    const ticket: Ticket = {
      id: randomUUID(),
      userId,
      originalText: data.message,
      status: TicketStatus.OPEN,
      createdAt: new Date(),
    };

    await query(
      'INSERT INTO tickets (id, user_id, original_text, status, created_at) VALUES ($1, $2, $3, $4, $5)',
      [ticket.id, ticket.userId, ticket.originalText, ticket.status, ticket.createdAt]
    );

    logger.info({ ticketId: ticket.id }, 'Ticket created in Postgres');

    // Dispatch background job
    await this.jobQueue.add('process-ticket', {
      ticketId: ticket.id,
      message: data.message,
      requestAudio: data.requestAudio,
      userId,
    });

    logger.info({ ticketId: ticket.id }, 'Ticket submitted to processing queue');

    return ticket;
  }

  async getTicket(id: string): Promise<Ticket | undefined> {
    const res = await query('SELECT * FROM tickets WHERE id = $1', [id]);
    if (res.rows[0]) {
      const row = res.rows[0];
      return {
        id: row.id,
        userId: row.user_id,
        originalText: row.original_text,
        detectedLanguage: row.detected_language,
        translatedText: row.translated_text,
        aiResponse: row.ai_response,
        audioUrl: row.audio_url,
        status: row.status as TicketStatus,
        createdAt: row.created_at,
      };
    }
    return undefined;
  }

  async updateTicket(id: string, updates: Partial<Ticket>): Promise<Ticket | undefined> {
    const entries = Object.entries(updates);
    if (entries.length === 0) return this.getTicket(id);

    // Map camelCase to snake_case for columns
    const mapping: Record<string, string> = {
      userId: 'user_id',
      originalText: 'original_text',
      detectedLanguage: 'detected_language',
      translatedText: 'translated_text',
      aiResponse: 'ai_response',
      audioUrl: 'audio_url',
      status: 'status',
      createdAt: 'created_at'
    };

    const setClause = entries
      .map(([key, _], idx) => `${mapping[key] || key} = $${idx + 2}`)
      .join(', ');
    const values = entries.map(([_, val]) => val);

    await query(`UPDATE tickets SET ${setClause} WHERE id = $1`, [id, ...values]);
    return this.getTicket(id);
  }
}

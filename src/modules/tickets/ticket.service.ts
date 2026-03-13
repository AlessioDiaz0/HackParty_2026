import { Queue } from 'bullmq';
import { CreateTicketDTO, Ticket, TicketStatus } from './ticket.schema';
import { randomUUID } from 'crypto';
import { logger } from '../../core/logger';

// In-memory store for prototype
const DB: Ticket[] = [];

export class TicketService {
  constructor(private readonly jobQueue: Queue) {}

  async createTicket(userId: string, data: CreateTicketDTO): Promise<Ticket> {
    const ticket: Ticket = {
      id: randomUUID(),
      userId,
      originalText: data.message,
      status: TicketStatus.OPEN,
      createdAt: new Date(),
    };

    DB.push(ticket);
    logger.info({ ticketId: ticket.id }, 'Ticket created in DB');

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
    return DB.find((t) => t.id === id);
  }

  async updateTicket(id: string, updates: Partial<Ticket>): Promise<Ticket | undefined> {
    const ticketIdx = DB.findIndex((t) => t.id === id);
    if (ticketIdx > -1) {
      DB[ticketIdx] = { ...DB[ticketIdx], ...updates };
      return DB[ticketIdx];
    }
    return undefined;
  }
}

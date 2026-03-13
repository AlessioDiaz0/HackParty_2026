import { z } from 'zod';

export const createTicketSchema = z.object({
  message: z.string().min(5, 'Message must be at least 5 characters long'),
  requestAudio: z.boolean().optional().default(false),
});

export type CreateTicketDTO = z.infer<typeof createTicketSchema>;

export enum TicketStatus {
  OPEN = 'OPEN',
  IN_PROGRESS = 'IN_PROGRESS',
  RESOLVED = 'RESOLVED',
}

export interface Ticket {
  id: string;
  userId: string;
  originalText: string;
  detectedLanguage?: string;
  translatedText?: string;
  aiResponse?: string;
  audioUrl?: string;
  status: TicketStatus;
  createdAt: Date;
}

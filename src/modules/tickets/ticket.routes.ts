import { FastifyInstance } from 'fastify';
import { TicketService } from './ticket.service';
import { createTicketSchema } from './ticket.schema';

export async function ticketRoutes(fastify: FastifyInstance, opts: { ticketService: TicketService }) {
  fastify.post(
    '/tickets',
    {
      // Using an inline type check here instead of Zod Fastify plugin for simplicity
      // In a real app we'd use fastify-type-provider-zod
      preValidation: async (request, reply) => {
        const parsed = createTicketSchema.safeParse(request.body);
        if (!parsed.success) {
          reply.code(400).send({ error: 'Validation failed', details: parsed.error });
        }
      }
    },
    async (request, reply) => {
      // @ts-ignore - Assuming fastify-jwt handles request.user
      const userId = request.user?.id || 'anonymous';
      const parsedBody = createTicketSchema.parse(request.body);

      const ticket = await opts.ticketService.createTicket(userId, parsedBody);

      return reply.code(202).send({
        success: true,
        ticketId: ticket.id,
        message: 'Ticket created. AI is analyzing your request.',
      });
    }
  );

  fastify.get('/tickets/:id', async (request, reply) => {
    const { id } = request.params as { id: string };
    const ticket = await opts.ticketService.getTicket(id);
    
    if (!ticket) {
      return reply.code(404).send({ error: 'Ticket not found' });
    }
    
    return ticket;
  });
}

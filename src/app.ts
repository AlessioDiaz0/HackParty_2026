import fastify from 'fastify';
import fastifyJwt from '@fastify/jwt';
import { config } from './core/config';
import { logger } from './core/logger';
import { ticketRoutes } from './modules/tickets/ticket.routes';
import { TicketService } from './modules/tickets/ticket.service';
import { ticketQueue } from './core/eventBus';

export const buildApp = () => {
  const app = fastify({ logger: false }); // Use custom pino manually or fastify default

  app.register(fastifyJwt, { secret: config.JWT_SECRET });

  // Mock Authentication decorator
  // app.decorateRequest('user', null as any);
  app.addHook('onRequest', async (request, reply) => {
    try {
      // For the hackathon, hardcode user auth bypass
      request.user = { id: 'mock-user-123', name: 'HackParty Maker' };
    } catch (err) {
      reply.send(err);
    }
  });

  // DI Setup
  const ticketService = new TicketService(ticketQueue);

  // Register routes
  app.register(ticketRoutes, { ticketService, prefix: '/api' });

  app.get('/health', async () => ({ status: 'ok' }));

  return { app, ticketService };
};

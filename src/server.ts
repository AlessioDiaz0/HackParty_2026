import { buildApp } from './app';
import { config } from './core/config';
import { logger } from './core/logger';
import { OpenAIProvider } from './modules/ai/openai.provider';
import { AIService } from './modules/ai/ai.service';
import { languageDetector } from './modules/i18n/detector';
import { translatorService } from './modules/i18n/translator';
import { ttsService } from './modules/speech/tts.service';
import { startTicketWorker } from './workers/ticket.worker';

const start = async () => {
  const { app, ticketService } = buildApp();
  
  // Initialize AI providers
  const aiProvider = new OpenAIProvider(config.OPENAI_API_KEY);
  const aiService = new AIService(aiProvider);

  // Start background worker
  startTicketWorker(
    ticketService,
    aiService,
    languageDetector,
    translatorService,
    ttsService
  );

  try {
    await app.listen({ port: parseInt(config.PORT, 10), host: '0.0.0.0' });
    logger.info(`🚀 Fastify HackParty Server listening on port ${config.PORT}`);
    logger.info(`Try: POST http://localhost:${config.PORT}/api/tickets`);
  } catch (err) {
    logger.error(err);
    process.exit(1);
  }
};

start();

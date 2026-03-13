import { createWorker } from '../core/eventBus';
import { TicketService } from '../modules/tickets/ticket.service';
import { AIService } from '../modules/ai/ai.service';
import { LanguageDetector } from '../modules/i18n/detector';
import { TranslatorService } from '../modules/i18n/translator';
import { TTSService } from '../modules/speech/tts.service';
import { logger } from '../core/logger';
import { TicketStatus } from '../modules/tickets/ticket.schema';

export const startTicketWorker = (
  ticketService: TicketService,
  aiService: AIService,
  languageDetector: LanguageDetector,
  translatorService: TranslatorService,
  ttsService: TTSService
) => {
  return createWorker('ticket-processing', async (job) => {
    const { ticketId, message, requestAudio } = job.data;
    logger.info({ ticketId }, 'Starting background ticket processing');

    try {
      // 1. Mark in progress
      await ticketService.updateTicket(ticketId, { status: TicketStatus.IN_PROGRESS });

      // 2. Detect language
      const language = languageDetector.detectLanguage(message);
      logger.info({ ticketId, language }, 'Language detected');

      // 3. Translation (optional to internal systems if needed, skipping directly to AI here for prototype)
      const translatedInfo = await translatorService.translateToEnglish(message, language);

      // 4. AI response gen
      const aiReplyText = await aiService.generateTicketSupportReply(translatedInfo, language);

      // 5. TTS generation
      let audioUrl = undefined;
      if (requestAudio) {
        audioUrl = await ttsService.generateAudioUrl(aiReplyText, ticketId);
      }

      // 6. Complete and save
      await ticketService.updateTicket(ticketId, {
        status: TicketStatus.RESOLVED,
        detectedLanguage: language,
        aiResponse: aiReplyText,
        audioUrl,
      });

      logger.info({ ticketId }, 'Background ticket processing finished successfully');

    } catch (error) {
      logger.error({ ticketId, err: error }, 'Failed to process ticket');
      throw error;
    }
  });
};

import { logger } from '../../core/logger';

export class TranslatorService {
  async translateToEnglish(text: string, sourceLang: string): Promise<string> {
    if (sourceLang === 'en') return text;
    
    logger.info({ sourceLang }, 'Simulating translation to English');
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    return `[Translated from ${sourceLang}]: ${text}`;
  }
}

export const translatorService = new TranslatorService();

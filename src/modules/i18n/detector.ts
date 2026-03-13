import { franc } from 'franc-min';
import { logger } from '../../core/logger';

export class LanguageDetector {
  detectLanguage(text: string): string {
    const lang3 = franc(text, { minLength: 5 });
    logger.debug({ textLength: text.length, lang3 }, 'Language detected');
    
    // mapping to 2 char code for simplicity
    const map: Record<string, string> = {
      ita: 'it',
      fra: 'fr',
      spa: 'es',
      deu: 'de',
      eng: 'en'
    };
    
    return map[lang3] || 'en';
  }
}

export const languageDetector = new LanguageDetector();

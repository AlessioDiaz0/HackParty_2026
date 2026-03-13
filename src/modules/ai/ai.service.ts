import { AIProvider } from './ai.provider';
import { getSupportSystemPrompt } from './prompts';

export class AIService {
  constructor(private readonly provider: AIProvider) {}

  async generateTicketSupportReply(userMessage: string, languageCode: string): Promise<string> {
    const systemPrompt = getSupportSystemPrompt(languageCode);
    
    const reply = await this.provider.generateReply({
      systemPrompt,
      userMessage,
    });

    return reply;
  }
}

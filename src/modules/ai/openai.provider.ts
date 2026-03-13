import { AIProvider, GenerateAIResponseArgs } from './ai.provider';
import { logger } from '../../core/logger';

// A mock OpenAI provider for hackathon prototyping
// Replace with actual `openai` edge client when ready
export class OpenAIProvider implements AIProvider {
  name = 'OpenAI_Mock';

  constructor(private readonly apiKey?: string) {}

  async generateReply({ systemPrompt, userMessage }: GenerateAIResponseArgs): Promise<string> {
    logger.info({ provider: this.name }, 'Simulating OpenAI completion response');
    
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    // Mock completion logic
    if (userMessage.toLowerCase().includes('password')) {
      return 'To reset your password, please visit your account settings page and click on "Forgot Password".';
    }

    return 'Thank you for your message. As an AI assistant, I can see your request but cannot solve it immediately. A human agent will contact you shortly.';
  }
}

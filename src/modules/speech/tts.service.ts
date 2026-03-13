import { logger } from '../../core/logger';

export class TTSService {
  constructor(private readonly apiKey?: string) {}

  async generateAudioUrl(text: string, ticketId: string): Promise<string> {
    logger.info({ ticketId }, 'Simulating TTS Generation...');
    
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    const fileName = `tts-${ticketId}-${Date.now()}.mp3`;
    const url = `https://storage.hackparty.local/audio/${fileName}`;
    
    logger.info({ ticketId, url }, 'TTS Generation complete');
    return url;
  }
}

export const ttsService = new TTSService(process.env.ELEVENLABS_API_KEY);

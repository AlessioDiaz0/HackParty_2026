export interface GenerateAIResponseArgs {
  systemPrompt: string;
  userMessage: string;
}

export interface AIProvider {
  name: string;
  generateReply(args: GenerateAIResponseArgs): Promise<string>;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface SearchResult {
  text: string;
  metadata: {
    similarity_score: number;
  };
}

export interface SourceLink {
  provider: string;
  link: string;
  metadata?: Record<string, string>;
}

export interface ChatResponse {
  answer: string;
  sources: SearchResult[];
  source_links?: SourceLink[];
  context_chunks: string[];
  conversation_id: string;
  provider?: string;
}

export interface Statistics {
  embedding_count: number;
  conversation_count: number;
}

export interface ConversationTurn {
  query: string;
  response: string;
  timestamp: string;
}

export interface Conversation {
  id: string;
  turns: ConversationTurn[];
} 
// Chat interface TypeScript type definitions template
// Replace {{PREFIX}} with your project prefix (e.g., "App", "Widget")

export interface {{PREFIX}}ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  content_type: 'text' | 'markdown' | 'code' | 'image';
  timestamp: string; // ISO 8601
  status: 'sending' | 'sent' | 'delivered' | 'error';
  metadata?: {
    citations?: {{PREFIX}}Citation[];
    attachments?: {{PREFIX}}Attachment[];
    tokens_used?: number;
  };
}

export interface {{PREFIX}}ChatEvent {
  type: 'message' | 'typing' | 'status' | 'error' | 'connection';
  payload: {{PREFIX}}ChatMessage | TypingState | ConnectionState | ErrorPayload;
}

export type ConnectionStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'error';

export type ChatSessionState =
  | 'idle'
  | 'composing'
  | 'waiting'
  | 'streaming'
  | 'error';

export interface {{PREFIX}}Citation {
  title: string;
  url: string;
  snippet?: string;
}

export interface {{PREFIX}}Attachment {
  id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  url: string;
}

export interface TypingState {
  user_id: string;
  is_typing: boolean;
}

export interface ConnectionState {
  status: ConnectionStatus;
  error?: string;
}

export interface ErrorPayload {
  code: string;
  message: string;
  retryable: boolean;
}

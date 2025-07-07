/**
 * EVA-Dev Frontend Type Definitions
 */

// =============================================================================
// Chat Types
// =============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  type?: 'text' | 'voice';
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
  stream?: boolean;
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  messageId: string;
}

// =============================================================================
// Voice Types
// =============================================================================

export interface VoiceRequest {
  audioData: string; // Base64 encoded
  sessionId?: string;
  format?: string;
}

export interface VoiceResponse {
  transcription: string;
  responseText: string;
  responseAudio: string; // Base64 encoded
  sessionId: string;
  messageId: string;
}

export interface TTSRequest {
  text: string;
  voice?: string;
}

export interface STTResponse {
  transcription: string;
  confidence: number;
  language: string;
}

// =============================================================================
// Audio Types
// =============================================================================

export interface AudioRecorderState {
  isRecording: boolean;
  isProcessing: boolean;
  audioBlob: Blob | null;
  duration: number;
  error: string | null;
}

export interface AudioConfig {
  sampleRate: number;
  channels: number;
  bitsPerSample: number;
  maxDuration: number;
  silenceTimeout: number;
}

// =============================================================================
// UI Types
// =============================================================================

export interface ChatWidgetProps {
  apiUrl?: string;
  theme?: 'light' | 'dark';
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  initialMessage?: string;
  showVoiceButton?: boolean;
  autoOpen?: boolean;
  className?: string;
}

export interface MessageBubbleProps {
  message: ChatMessage;
  isLast?: boolean;
  onRetry?: () => void;
}

export interface VoiceButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
  disabled?: boolean;
}

// =============================================================================
// API Types
// =============================================================================

export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: any;
}

export interface HealthCheckResponse {
  status: string;
  environment: string;
  version: string;
  services?: {
    api: string;
    azureSpeech: string;
    claudeApi: string;
    redis: string;
  };
}

// =============================================================================
// Configuration Types
// =============================================================================

export interface AppConfig {
  apiUrl: string;
  websocketUrl: string;
  environment: 'development' | 'production';
  features: {
    voiceEnabled: boolean;
    streamingEnabled: boolean;
    historyEnabled: boolean;
  };
  audio: AudioConfig;
}

// =============================================================================
// Event Types
// =============================================================================

export interface ChatEvent {
  type: 'message' | 'typing' | 'error' | 'connected' | 'disconnected';
  data?: any;
  timestamp: string;
}

export interface VoiceEvent {
  type: 'recording_start' | 'recording_stop' | 'processing' | 'complete' | 'error';
  data?: any;
  timestamp: string;
}

// =============================================================================
// Hook Types
// =============================================================================

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sendMessage: (message: string) => Promise<void>;
  sendVoiceMessage: (audioBlob: Blob) => Promise<void>;
  clearHistory: () => void;
  sessionId: string;
}

export interface UseAudioRecorderReturn {
  state: AudioRecorderState;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  clearRecording: () => void;
  isSupported: boolean;
}

export interface UseWebSocketReturn {
  isConnected: boolean;
  sendMessage: (message: any) => void;
  lastMessage: any;
  error: string | null;
}

// =============================================================================
// Utility Types
// =============================================================================

export type DeepPartial<T> = {
  [P in keyof T]?: DeepPartial<T[P]>;
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// =============================================================================
// Component State Types
// =============================================================================

export interface ChatWidgetState {
  isOpen: boolean;
  isMinimized: boolean;
  currentSession: ChatSession | null;
  isConnected: boolean;
  hasUnreadMessages: boolean;
}

export interface VoiceControlState {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  volume: number;
  error: string | null;
}

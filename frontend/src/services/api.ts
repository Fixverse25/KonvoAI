/**
 * EVA-Dev API Service
 * Handles all API communications with the backend
 */

import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  VoiceRequest,
  VoiceResponse,
  TTSRequest,
  STTResponse,
  HealthCheckResponse,
  ApiResponse,
  ChatMessage,
} from '../types';

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // =============================================================================
  // Health Check
  // =============================================================================

  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.client.get<HealthCheckResponse>('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async detailedHealthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.client.get<HealthCheckResponse>('/api/v1/health/detailed');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =============================================================================
  // Chat API
  // =============================================================================

  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await this.client.post<ChatResponse>('/api/v1/chat', request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async streamChatMessage(request: ChatRequest): Promise<ReadableStream<Uint8Array>> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      return response.body;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    try {
      const response = await this.client.get<ChatMessage[]>(`/api/v1/chat/history/${sessionId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async clearChatHistory(sessionId: string): Promise<void> {
    try {
      await this.client.delete(`/api/v1/chat/history/${sessionId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =============================================================================
  // Voice API
  // =============================================================================

  async speechToText(audioFile: File): Promise<STTResponse> {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);

      const response = await this.client.post<STTResponse>(
        '/api/v1/voice/speech-to-text',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async textToSpeech(request: TTSRequest): Promise<Blob> {
    try {
      const response = await this.client.post('/api/v1/voice/text-to-speech', request, {
        responseType: 'blob',
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async voiceChat(request: VoiceRequest): Promise<VoiceResponse> {
    try {
      const response = await this.client.post<VoiceResponse>('/api/v1/voice/voice-chat', request);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async testVoiceServices(): Promise<any> {
    try {
      const response = await this.client.get('/api/v1/voice/test-services');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // =============================================================================
  // Utility Methods
  // =============================================================================

  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.error || error.message;
      return new Error(`API Error (${error.response.status}): ${message}`);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network Error: No response from server');
    } else {
      // Something else happened
      return new Error(`Request Error: ${error.message}`);
    }
  }

  // Convert blob to base64
  async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove data URL prefix (e.g., "data:audio/wav;base64,")
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // Convert base64 to blob
  base64ToBlob(base64: string, mimeType: string = 'audio/wav'): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  // Get WebSocket URL
  getWebSocketUrl(): string {
    const wsProtocol = this.baseURL.startsWith('https') ? 'wss' : 'ws';
    return this.baseURL.replace(/^https?/, wsProtocol);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;

/**
 * Chat Hook
 * Manages chat state, message sending, and conversation history
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ChatMessage, UseChatReturn } from '../types';
import { apiService } from '../services/api';

export const useChat = (initialSessionId?: string): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState<string>(initialSessionId || uuidv4());

  const abortControllerRef = useRef<AbortController | null>(null);

  // Load chat history on mount
  useEffect(() => {
    if (initialSessionId) {
      loadChatHistory();
    }
  }, [initialSessionId]);

  // Load chat history from backend
  const loadChatHistory = useCallback(async () => {
    try {
      const history = await apiService.getChatHistory(sessionId);
      setMessages(history);
    } catch (err) {
      console.error('Failed to load chat history:', err);
      // Don't set error state for history loading failure
    }
  }, [sessionId]);

  // Add message to chat
  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: uuidv4(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  }, []);

  // Update message
  const updateMessage = useCallback((messageId: string, updates: Partial<ChatMessage>) => {
    setMessages(prev =>
      prev.map(msg =>
        msg.id === messageId ? { ...msg, ...updates } : msg
      )
    );
  }, []);

  // Send text message
  const sendMessage = useCallback(async (content: string): Promise<void> => {
    if (!content.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    const userMessage = addMessage({
      role: 'user',
      content: content.trim(),
      type: 'text',
    });

    try {
      // Cancel any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      // Send message to backend
      const response = await apiService.sendChatMessage({
        message: content.trim(),
        sessionId,
        stream: false,
      });

      // Add assistant response
      addMessage({
        role: 'assistant',
        content: response.response,
        type: 'text',
      });

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Send message error:', err);

      // Add error message
      addMessage({
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try again.',
        type: 'text',
      });
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId, addMessage]);

  // Send streaming message
  const sendStreamingMessage = useCallback(async (content: string): Promise<void> => {
    if (!content.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message
    addMessage({
      role: 'user',
      content: content.trim(),
      type: 'text',
    });

    // Add placeholder assistant message
    const assistantMessage = addMessage({
      role: 'assistant',
      content: '',
      type: 'text',
      isStreaming: true,
    });

    try {
      // Cancel any ongoing request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }

      abortControllerRef.current = new AbortController();

      // Get streaming response
      const stream = await apiService.streamChatMessage({
        message: content.trim(),
        sessionId,
        stream: true,
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            if (data === '[DONE]') {
              // Streaming complete
              updateMessage(assistantMessage.id, { isStreaming: false });
              break;
            }

            if (data.trim()) {
              accumulatedContent += data;
              updateMessage(assistantMessage.id, { content: accumulatedContent });
            }
          }
        }
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      console.error('Send streaming message error:', err);

      // Update assistant message with error
      updateMessage(assistantMessage.id, {
        content: 'I apologize, but I encountered an error. Please try again.',
        isStreaming: false,
      });
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId, addMessage, updateMessage]);

  // Send voice message
  const sendVoiceMessage = useCallback(async (audioBlob: Blob): Promise<void> => {
    setError(null);
    setIsLoading(true);

    try {
      // Convert audio blob to base64
      const base64Audio = await apiService.blobToBase64(audioBlob);

      // Send voice message to backend
      const response = await apiService.voiceChat({
        audioData: base64Audio,
        sessionId,
        format: 'webm',
      });

      // Add user message (transcription)
      addMessage({
        role: 'user',
        content: response.transcription,
        type: 'voice',
      });

      // Add assistant response
      const assistantMessage = addMessage({
        role: 'assistant',
        content: response.responseText,
        type: 'voice',
      });

      // Play response audio
      if (response.responseAudio) {
        const audioBlob = apiService.base64ToBlob(response.responseAudio, 'audio/wav');
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.play().catch(err => {
          console.error('Failed to play response audio:', err);
        });

        // Clean up URL after playing
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
        };
      }

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to process voice message';
      setError(errorMessage);
      console.error('Send voice message error:', err);

      // Add error message
      addMessage({
        role: 'assistant',
        content: 'I apologize, but I had trouble processing your voice message. Please try again.',
        type: 'text',
      });
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, addMessage]);

  // Clear chat history
  const clearHistory = useCallback(async () => {
    try {
      await apiService.clearChatHistory(sessionId);
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to clear chat history:', err);
      setError('Failed to clear chat history');
    }
  }, [sessionId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage: sendStreamingMessage, // Use streaming by default
    sendVoiceMessage,
    clearHistory,
    sessionId,
  };
};

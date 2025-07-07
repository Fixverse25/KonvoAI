/**
 * Chat Widget Component
 * Main chat interface with text and voice capabilities
 */

import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { MessageCircle, X, Minimize2, Maximize2, Mic, MicOff, Send } from 'lucide-react';
import { ChatWidgetProps, ChatWidgetState } from '../types';
import { useChat } from '../hooks/useChat';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import MessageBubble from './MessageBubble';
import VoiceButton from './VoiceButton';

const ChatWidget: React.FC<ChatWidgetProps> = ({
  apiUrl,
  theme = 'light',
  position = 'bottom-right',
  initialMessage,
  showVoiceButton = true,
  autoOpen = false,
  className,
}) => {
  const [widgetState, setWidgetState] = useState<ChatWidgetState>({
    isOpen: autoOpen,
    isMinimized: false,
    currentSession: null,
    isConnected: true,
    hasUnreadMessages: false,
  });

  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const { messages, isLoading, error, sendMessage, sendVoiceMessage, clearHistory, sessionId } = useChat();
  const { state: audioState, startRecording, stopRecording, isSupported: isAudioSupported } = useAudioRecorder();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Send initial message if provided
  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      sendMessage(initialMessage);
    }
  }, [initialMessage, messages.length, sendMessage]);

  // Focus input when widget opens
  useEffect(() => {
    if (widgetState.isOpen && !widgetState.isMinimized) {
      inputRef.current?.focus();
    }
  }, [widgetState.isOpen, widgetState.isMinimized]);

  // Handle text message send
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const message = inputValue.trim();
    setInputValue('');
    await sendMessage(message);
  };

  // Handle voice recording
  const handleVoiceToggle = async () => {
    if (audioState.isRecording) {
      const audioBlob = await stopRecording();
      if (audioBlob) {
        await sendVoiceMessage(audioBlob);
      }
    } else {
      await startRecording();
    }
  };

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Toggle widget open/close
  const toggleWidget = () => {
    setWidgetState(prev => ({
      ...prev,
      isOpen: !prev.isOpen,
      hasUnreadMessages: false,
    }));
  };

  // Toggle minimize/maximize
  const toggleMinimize = () => {
    setWidgetState(prev => ({
      ...prev,
      isMinimized: !prev.isMinimized,
    }));
  };

  return (
    <WidgetContainer className={className} position={position} theme={theme}>
      {/* Chat Button */}
      {!widgetState.isOpen && (
        <ChatButton onClick={toggleWidget} theme={theme} hasUnread={widgetState.hasUnreadMessages}>
          <MessageCircle size={24} />
          {widgetState.hasUnreadMessages && <UnreadIndicator />}
        </ChatButton>
      )}

      {/* Chat Window */}
      {widgetState.isOpen && (
        <ChatWindow theme={theme} isMinimized={widgetState.isMinimized}>
          {/* Header */}
          <ChatHeader theme={theme}>
            <HeaderTitle>
              <MessageCircle size={20} />
              <span>EVA-Dev</span>
              {!widgetState.isConnected && <DisconnectedIndicator>●</DisconnectedIndicator>}
            </HeaderTitle>
            <HeaderActions>
              <HeaderButton onClick={toggleMinimize} theme={theme}>
                {widgetState.isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
              </HeaderButton>
              <HeaderButton onClick={toggleWidget} theme={theme}>
                <X size={16} />
              </HeaderButton>
            </HeaderActions>
          </ChatHeader>

          {/* Messages Area */}
          {!widgetState.isMinimized && (
            <>
              <MessagesContainer theme={theme}>
                {messages.length === 0 && (
                  <WelcomeMessage theme={theme}>
                    <h3>👋 Hello! I'm EVA-Dev</h3>
                    <p>I'm here to help you with EV charging questions and support. You can type your message or use the voice button to speak with me.</p>
                  </WelcomeMessage>
                )}
                
                {messages.map((message, index) => (
                  <MessageBubble
                    key={message.id}
                    message={message}
                    isLast={index === messages.length - 1}
                  />
                ))}
                
                {isLoading && (
                  <TypingIndicator theme={theme}>
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span>EVA-Dev is typing...</span>
                  </TypingIndicator>
                )}
                
                {error && (
                  <ErrorMessage theme={theme}>
                    <span>⚠️ {error}</span>
                    <button onClick={() => window.location.reload()}>Retry</button>
                  </ErrorMessage>
                )}
                
                <div ref={messagesEndRef} />
              </MessagesContainer>

              {/* Input Area */}
              <InputContainer theme={theme}>
                <InputWrapper>
                  <TextInput
                    ref={inputRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    disabled={isLoading || audioState.isRecording}
                    theme={theme}
                  />
                  
                  {showVoiceButton && isAudioSupported && (
                    <VoiceButton
                      isRecording={audioState.isRecording}
                      isProcessing={audioState.isProcessing || isLoading}
                      onStartRecording={startRecording}
                      onStopRecording={stopRecording}
                      disabled={isLoading}
                    />
                  )}
                  
                  <SendButton
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading || audioState.isRecording}
                    theme={theme}
                  >
                    <Send size={16} />
                  </SendButton>
                </InputWrapper>
                
                {audioState.isRecording && (
                  <RecordingIndicator theme={theme}>
                    <div className="recording-pulse" />
                    <span>Recording... (speak now, I'll stop after 3s of silence)</span>
                    <span>{(audioState.duration / 1000).toFixed(1)}s</span>
                  </RecordingIndicator>
                )}
              </InputContainer>
            </>
          )}
        </ChatWindow>
      )}
    </WidgetContainer>
  );
};

// Styled Components
const WidgetContainer = styled.div<{ position: string; theme: string }>`
  position: fixed;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  
  ${({ position }) => {
    switch (position) {
      case 'bottom-right':
        return 'bottom: 20px; right: 20px;';
      case 'bottom-left':
        return 'bottom: 20px; left: 20px;';
      case 'top-right':
        return 'top: 20px; right: 20px;';
      case 'top-left':
        return 'top: 20px; left: 20px;';
      default:
        return 'bottom: 20px; right: 20px;';
    }
  }}
`;

const ChatButton = styled.button<{ theme: string; hasUnread: boolean }>`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: ${({ theme }) => theme === 'dark' ? '#2563eb' : '#3b82f6'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  ${({ hasUnread }) => hasUnread && `
    animation: pulse 2s infinite;
  `}

  @keyframes pulse {
    0% { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
    50% { box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    100% { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); }
  }
`;

const UnreadIndicator = styled.div`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
`;

const ChatWindow = styled.div<{ theme: string; isMinimized: boolean }>`
  width: 380px;
  height: ${({ isMinimized }) => isMinimized ? 'auto' : '500px'};
  background: ${({ theme }) => theme === 'dark' ? '#1f2937' : '#ffffff'};
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid ${({ theme }) => theme === 'dark' ? '#374151' : '#e5e7eb'};

  @media (max-width: 480px) {
    width: calc(100vw - 40px);
    height: ${({ isMinimized }) => isMinimized ? 'auto' : 'calc(100vh - 40px)'};
  }
`;

const ChatHeader = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: ${({ theme }) => theme === 'dark' ? '#374151' : '#f9fafb'};
  border-bottom: 1px solid ${({ theme }) => theme === 'dark' ? '#4b5563' : '#e5e7eb'};
`;

const HeaderTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: ${({ theme }) => theme === 'dark' ? '#f9fafb' : '#111827'};
`;

const DisconnectedIndicator = styled.span`
  color: #ef4444;
  font-size: 12px;
  margin-left: 4px;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 4px;
`;

const HeaderButton = styled.button<{ theme: string }>`
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${({ theme }) => theme === 'dark' ? '#9ca3af' : '#6b7280'};
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme === 'dark' ? '#4b5563' : '#e5e7eb'};
    color: ${({ theme }) => theme === 'dark' ? '#f9fafb' : '#111827'};
  }
`;

const MessagesContainer = styled.div<{ theme: string }>`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: ${({ theme }) => theme === 'dark' ? '#1f2937' : '#ffffff'};
`;

const WelcomeMessage = styled.div<{ theme: string }>`
  text-align: center;
  padding: 20px;
  color: ${({ theme }) => theme === 'dark' ? '#d1d5db' : '#6b7280'};

  h3 {
    margin: 0 0 8px 0;
    color: ${({ theme }) => theme === 'dark' ? '#f9fafb' : '#111827'};
  }

  p {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
  }
`;

const TypingIndicator = styled.div<{ theme: string }>`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin: 8px 0;
  background: ${({ theme }) => theme === 'dark' ? '#374151' : '#f3f4f6'};
  border-radius: 18px;
  color: ${({ theme }) => theme === 'dark' ? '#d1d5db' : '#6b7280'};
  font-size: 14px;

  .typing-dots {
    display: flex;
    gap: 4px;

    span {
      width: 6px;
      height: 6px;
      background: currentColor;
      border-radius: 50%;
      animation: typing 1.4s infinite ease-in-out;

      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
    }
  }

  @keyframes typing {
    0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
    40% { transform: scale(1); opacity: 1; }
  }
`;

const ErrorMessage = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  margin: 8px 0;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;

  button {
    background: #dc2626;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;

    &:hover {
      background: #b91c1c;
    }
  }
`;

const InputContainer = styled.div<{ theme: string }>`
  padding: 16px 20px;
  background: ${({ theme }) => theme === 'dark' ? '#374151' : '#f9fafb'};
  border-top: 1px solid ${({ theme }) => theme === 'dark' ? '#4b5563' : '#e5e7eb'};
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 8px;
  align-items: flex-end;
`;

const TextInput = styled.input<{ theme: string }>`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid ${({ theme }) => theme === 'dark' ? '#4b5563' : '#d1d5db'};
  border-radius: 24px;
  background: ${({ theme }) => theme === 'dark' ? '#1f2937' : '#ffffff'};
  color: ${({ theme }) => theme === 'dark' ? '#f9fafb' : '#111827'};
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;

  &:focus {
    border-color: #3b82f6;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &::placeholder {
    color: ${({ theme }) => theme === 'dark' ? '#9ca3af' : '#9ca3af'};
  }
`;

const SendButton = styled.button<{ theme: string }>`
  width: 40px;
  height: 40px;
  border: none;
  background: ${({ theme, disabled }) => disabled ? '#9ca3af' : '#3b82f6'};
  color: white;
  border-radius: 50%;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    background: #2563eb;
    transform: scale(1.05);
  }
`;

const RecordingIndicator = styled.div<{ theme: string }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding: 8px 12px;
  background: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 8px;
  color: #92400e;
  font-size: 12px;

  .recording-pulse {
    width: 8px;
    height: 8px;
    background: #ef4444;
    border-radius: 50%;
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

export default ChatWidget;

/**
 * Message Bubble Component
 * Displays individual chat messages with proper styling
 */

import React from 'react';
import styled from 'styled-components';
import ReactMarkdown from 'react-markdown';
import { User, Bot, Volume2, RotateCcw } from 'lucide-react';
import { MessageBubbleProps } from '../types';

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isLast, onRetry }) => {
  const isUser = message.role === 'user';
  const isVoice = message.type === 'voice';

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <MessageContainer isUser={isUser} isLast={isLast}>
      <MessageWrapper isUser={isUser}>
        <Avatar isUser={isUser}>
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </Avatar>
        
        <MessageContent>
          <MessageBubbleStyled isUser={isUser} isStreaming={message.isStreaming}>
            {isVoice && (
              <VoiceIndicator>
                <Volume2 size={14} />
                <span>{isUser ? 'Voice message' : 'Voice response'}</span>
              </VoiceIndicator>
            )}
            
            <MessageText isUser={isUser}>
              {isUser ? (
                message.content
              ) : (
                <ReactMarkdown
                  components={{
                    // Custom components for markdown rendering
                    p: ({ children }) => <p style={{ margin: '0 0 8px 0' }}>{children}</p>,
                    ul: ({ children }) => <ul style={{ margin: '0 0 8px 0', paddingLeft: '16px' }}>{children}</ul>,
                    ol: ({ children }) => <ol style={{ margin: '0 0 8px 0', paddingLeft: '16px' }}>{children}</ol>,
                    li: ({ children }) => <li style={{ margin: '2px 0' }}>{children}</li>,
                    code: ({ children }) => (
                      <code style={{
                        background: isUser ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
                        padding: '2px 4px',
                        borderRadius: '3px',
                        fontSize: '0.9em',
                        fontFamily: 'monospace'
                      }}>
                        {children}
                      </code>
                    ),
                    pre: ({ children }) => (
                      <pre style={{
                        background: isUser ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.1)',
                        padding: '8px',
                        borderRadius: '6px',
                        overflow: 'auto',
                        fontSize: '0.9em',
                        fontFamily: 'monospace',
                        margin: '8px 0'
                      }}>
                        {children}
                      </pre>
                    ),
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              )}
            </MessageText>
            
            {message.isStreaming && (
              <StreamingIndicator>
                <div className="cursor" />
              </StreamingIndicator>
            )}
          </MessageBubbleStyled>
          
          <MessageMeta>
            <MessageTime>{formatTime(message.timestamp)}</MessageTime>
            {!isUser && onRetry && (
              <RetryButton onClick={onRetry} title="Regenerate response">
                <RotateCcw size={12} />
              </RetryButton>
            )}
          </MessageMeta>
        </MessageContent>
      </MessageWrapper>
    </MessageContainer>
  );
};

// Styled Components
const MessageContainer = styled.div<{ isUser: boolean; isLast?: boolean }>`
  display: flex;
  justify-content: ${({ isUser }) => isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: ${({ isLast }) => isLast ? '0' : '16px'};
`;

const MessageWrapper = styled.div<{ isUser: boolean }>`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  max-width: 80%;
  flex-direction: ${({ isUser }) => isUser ? 'row-reverse' : 'row'};
`;

const Avatar = styled.div<{ isUser: boolean }>`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${({ isUser }) => isUser ? '#3b82f6' : '#10b981'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4px;
`;

const MessageContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
`;

const MessageBubbleStyled = styled.div<{ isUser: boolean; isStreaming?: boolean }>`
  padding: 12px 16px;
  border-radius: 18px;
  background: ${({ isUser }) => isUser ? '#3b82f6' : '#f3f4f6'};
  color: ${({ isUser }) => isUser ? 'white' : '#111827'};
  word-wrap: break-word;
  position: relative;
  
  ${({ isUser }) => isUser ? `
    border-bottom-right-radius: 6px;
  ` : `
    border-bottom-left-radius: 6px;
  `}

  ${({ isStreaming }) => isStreaming && `
    &::after {
      content: '';
      position: absolute;
      bottom: 8px;
      right: 12px;
      width: 2px;
      height: 16px;
      background: currentColor;
      animation: blink 1s infinite;
    }
  `}

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
`;

const VoiceIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 4px;
  font-style: italic;
`;

const MessageText = styled.div<{ isUser: boolean }>`
  font-size: 14px;
  line-height: 1.4;
  
  /* Ensure proper text color for markdown content */
  * {
    color: inherit;
  }

  /* Style links */
  a {
    color: ${({ isUser }) => isUser ? 'rgba(255,255,255,0.9)' : '#3b82f6'};
    text-decoration: underline;
    
    &:hover {
      text-decoration: none;
    }
  }

  /* Style blockquotes */
  blockquote {
    border-left: 3px solid ${({ isUser }) => isUser ? 'rgba(255,255,255,0.3)' : '#d1d5db'};
    padding-left: 12px;
    margin: 8px 0;
    font-style: italic;
    opacity: 0.9;
  }

  /* Style headings */
  h1, h2, h3, h4, h5, h6 {
    margin: 8px 0 4px 0;
    font-weight: 600;
  }

  /* Remove margin from last element */
  > *:last-child {
    margin-bottom: 0 !important;
  }
`;

const StreamingIndicator = styled.div`
  display: inline-block;
  
  .cursor {
    display: inline-block;
    width: 2px;
    height: 16px;
    background: currentColor;
    animation: blink 1s infinite;
    margin-left: 2px;
  }
`;

const MessageMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
`;

const MessageTime = styled.span`
  font-size: 11px;
  color: #9ca3af;
  opacity: 0.7;
`;

const RetryButton = styled.button`
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: all 0.2s ease;

  &:hover {
    opacity: 1;
    background: rgba(0, 0, 0, 0.05);
  }
`;

export default MessageBubble;

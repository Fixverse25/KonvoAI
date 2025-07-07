/**
 * Voice Button Component
 * Push-to-talk button with visual feedback
 */

import React from 'react';
import styled from 'styled-components';
import { Mic, MicOff, Loader2 } from 'lucide-react';
import { VoiceButtonProps } from '../types';

const VoiceButton: React.FC<VoiceButtonProps> = ({
  isRecording,
  isProcessing,
  onStartRecording,
  onStopRecording,
  disabled = false,
}) => {
  const handleClick = () => {
    if (disabled || isProcessing) return;
    
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const getButtonState = () => {
    if (isProcessing) return 'processing';
    if (isRecording) return 'recording';
    return 'idle';
  };

  const getIcon = () => {
    if (isProcessing) return <Loader2 size={16} className="spin" />;
    if (isRecording) return <MicOff size={16} />;
    return <Mic size={16} />;
  };

  const getTooltip = () => {
    if (disabled) return 'Voice input not available';
    if (isProcessing) return 'Processing...';
    if (isRecording) return 'Click to stop recording';
    return 'Click to start recording';
  };

  return (
    <VoiceButtonContainer
      onClick={handleClick}
      disabled={disabled}
      state={getButtonState()}
      title={getTooltip()}
    >
      {getIcon()}
      
      {isRecording && (
        <>
          <RecordingRipple />
          <RecordingRipple delay={0.5} />
          <RecordingRipple delay={1} />
        </>
      )}
    </VoiceButtonContainer>
  );
};

// Styled Components
const VoiceButtonContainer = styled.button<{ state: string }>`
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  cursor: ${({ disabled }) => disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.2s ease;
  overflow: hidden;

  /* Base styles */
  background: ${({ state, disabled }) => {
    if (disabled) return '#9ca3af';
    switch (state) {
      case 'recording': return '#ef4444';
      case 'processing': return '#f59e0b';
      default: return '#10b981';
    }
  }};
  
  color: white;
  
  /* Hover effects */
  &:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  /* Active state */
  &:active:not(:disabled) {
    transform: scale(0.95);
  }

  /* Recording state animation */
  ${({ state }) => state === 'recording' && `
    animation: recordingPulse 2s infinite;
  `}

  /* Processing state animation */
  .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes recordingPulse {
    0% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
    }
    70% {
      box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
    }
    100% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
    }
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }
`;

const RecordingRipple = styled.div<{ delay?: number }>`
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  border: 2px solid #ef4444;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: ripple 2s infinite;
  animation-delay: ${({ delay = 0 }) => delay}s;
  opacity: 0;

  @keyframes ripple {
    0% {
      width: 40px;
      height: 40px;
      opacity: 1;
    }
    100% {
      width: 80px;
      height: 80px;
      opacity: 0;
    }
  }
`;

export default VoiceButton;

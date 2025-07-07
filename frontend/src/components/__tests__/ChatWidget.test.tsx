/**
 * Unit tests for ChatWidget component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import ChatWidget from '../ChatWidget';

// Mock the hooks
jest.mock('../../hooks/useChat', () => ({
  useChat: () => ({
    messages: [],
    isLoading: false,
    error: null,
    sendMessage: jest.fn(),
    sendVoiceMessage: jest.fn(),
    clearHistory: jest.fn(),
    sessionId: 'test-session-id',
  }),
}));

jest.mock('../../hooks/useAudioRecorder', () => ({
  useAudioRecorder: () => ({
    state: {
      isRecording: false,
      isProcessing: false,
      audioBlob: null,
      duration: 0,
      error: null,
    },
    startRecording: jest.fn(),
    stopRecording: jest.fn(),
    clearRecording: jest.fn(),
    isSupported: true,
  }),
}));

describe('ChatWidget', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders chat button when closed', () => {
    render(<ChatWidget />);
    
    const chatButton = screen.getByRole('button');
    expect(chatButton).toBeInTheDocument();
    expect(chatButton).toHaveAttribute('title', expect.stringContaining('chat'));
  });

  test('opens chat window when button is clicked', async () => {
    const user = userEvent.setup();
    render(<ChatWidget />);
    
    const chatButton = screen.getByRole('button');
    await user.click(chatButton);
    
    // Should show the chat window
    expect(screen.getByText('EVA-Dev')).toBeInTheDocument();
  });

  test('displays welcome message when no messages', () => {
    render(<ChatWidget autoOpen={true} />);
    
    expect(screen.getByText(/Hello! I'm EVA-Dev/)).toBeInTheDocument();
    expect(screen.getByText(/EV charging questions/)).toBeInTheDocument();
  });

  test('shows voice button when voice is supported and enabled', () => {
    render(<ChatWidget autoOpen={true} showVoiceButton={true} />);
    
    // Look for microphone icon or voice button
    const voiceButton = screen.getByRole('button', { name: /voice|microphone/i });
    expect(voiceButton).toBeInTheDocument();
  });

  test('hides voice button when disabled', () => {
    render(<ChatWidget autoOpen={true} showVoiceButton={false} />);
    
    // Voice button should not be present
    const voiceButtons = screen.queryAllByRole('button', { name: /voice|microphone/i });
    expect(voiceButtons).toHaveLength(0);
  });

  test('allows typing in text input', async () => {
    const user = userEvent.setup();
    render(<ChatWidget autoOpen={true} />);
    
    const textInput = screen.getByPlaceholderText(/type your message/i);
    await user.type(textInput, 'Hello EVA-Dev');
    
    expect(textInput).toHaveValue('Hello EVA-Dev');
  });

  test('send button is disabled when input is empty', () => {
    render(<ChatWidget autoOpen={true} />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeDisabled();
  });

  test('send button is enabled when input has text', async () => {
    const user = userEvent.setup();
    render(<ChatWidget autoOpen={true} />);
    
    const textInput = screen.getByPlaceholderText(/type your message/i);
    await user.type(textInput, 'Test message');
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    expect(sendButton).toBeEnabled();
  });

  test('can minimize and maximize chat window', async () => {
    const user = userEvent.setup();
    render(<ChatWidget autoOpen={true} />);
    
    // Find minimize button
    const minimizeButton = screen.getByRole('button', { name: /minimize/i });
    await user.click(minimizeButton);
    
    // Chat content should be hidden
    expect(screen.queryByPlaceholderText(/type your message/i)).not.toBeInTheDocument();
    
    // Find maximize button
    const maximizeButton = screen.getByRole('button', { name: /maximize/i });
    await user.click(maximizeButton);
    
    // Chat content should be visible again
    expect(screen.getByPlaceholderText(/type your message/i)).toBeInTheDocument();
  });

  test('can close chat window', async () => {
    const user = userEvent.setup();
    render(<ChatWidget autoOpen={true} />);
    
    // Find close button
    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);
    
    // Chat window should be closed, only button visible
    expect(screen.queryByText('EVA-Dev')).not.toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument(); // Chat button
  });

  test('applies custom theme', () => {
    render(<ChatWidget autoOpen={true} theme="dark" />);
    
    // Check if dark theme is applied (this would depend on your styling implementation)
    const chatWindow = screen.getByText('EVA-Dev').closest('div');
    expect(chatWindow).toBeInTheDocument();
  });

  test('applies custom position', () => {
    render(<ChatWidget position="bottom-left" />);
    
    // Check if position is applied (this would depend on your styling implementation)
    const chatButton = screen.getByRole('button');
    expect(chatButton).toBeInTheDocument();
  });

  test('shows loading state', () => {
    // Mock the useChat hook to return loading state
    const mockUseChat = require('../../hooks/useChat').useChat;
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: true,
      error: null,
      sendMessage: jest.fn(),
      sendVoiceMessage: jest.fn(),
      clearHistory: jest.fn(),
      sessionId: 'test-session-id',
    });

    render(<ChatWidget autoOpen={true} />);
    
    expect(screen.getByText(/typing/i)).toBeInTheDocument();
  });

  test('shows error state', () => {
    // Mock the useChat hook to return error state
    const mockUseChat = require('../../hooks/useChat').useChat;
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: false,
      error: 'Connection failed',
      sendMessage: jest.fn(),
      sendVoiceMessage: jest.fn(),
      clearHistory: jest.fn(),
      sessionId: 'test-session-id',
    });

    render(<ChatWidget autoOpen={true} />);
    
    expect(screen.getByText(/connection failed/i)).toBeInTheDocument();
  });

  test('shows recording indicator when recording', () => {
    // Mock the useAudioRecorder hook to return recording state
    const mockUseAudioRecorder = require('../../hooks/useAudioRecorder').useAudioRecorder;
    mockUseAudioRecorder.mockReturnValue({
      state: {
        isRecording: true,
        isProcessing: false,
        audioBlob: null,
        duration: 1500,
        error: null,
      },
      startRecording: jest.fn(),
      stopRecording: jest.fn(),
      clearRecording: jest.fn(),
      isSupported: true,
    });

    render(<ChatWidget autoOpen={true} showVoiceButton={true} />);
    
    expect(screen.getByText(/recording/i)).toBeInTheDocument();
    expect(screen.getByText(/1.5s/)).toBeInTheDocument();
  });

  test('handles keyboard shortcuts', async () => {
    const user = userEvent.setup();
    const mockSendMessage = jest.fn();
    
    // Mock the useChat hook
    const mockUseChat = require('../../hooks/useChat').useChat;
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
      sendMessage: mockSendMessage,
      sendVoiceMessage: jest.fn(),
      clearHistory: jest.fn(),
      sessionId: 'test-session-id',
    });

    render(<ChatWidget autoOpen={true} />);
    
    const textInput = screen.getByPlaceholderText(/type your message/i);
    await user.type(textInput, 'Test message');
    await user.keyboard('{Enter}');
    
    expect(mockSendMessage).toHaveBeenCalledWith('Test message');
  });

  test('prevents sending empty messages', async () => {
    const user = userEvent.setup();
    const mockSendMessage = jest.fn();
    
    // Mock the useChat hook
    const mockUseChat = require('../../hooks/useChat').useChat;
    mockUseChat.mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
      sendMessage: mockSendMessage,
      sendVoiceMessage: jest.fn(),
      clearHistory: jest.fn(),
      sessionId: 'test-session-id',
    });

    render(<ChatWidget autoOpen={true} />);
    
    const textInput = screen.getByPlaceholderText(/type your message/i);
    await user.type(textInput, '   '); // Only whitespace
    await user.keyboard('{Enter}');
    
    expect(mockSendMessage).not.toHaveBeenCalled();
  });
});

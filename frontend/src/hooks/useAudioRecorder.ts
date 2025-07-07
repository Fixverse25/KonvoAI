/**
 * Audio Recorder Hook
 * Handles audio recording with silence detection and push-to-talk functionality
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { AudioRecorderState, UseAudioRecorderReturn } from '../types';

const DEFAULT_CONFIG = {
  sampleRate: 16000,
  channels: 1,
  bitsPerSample: 16,
  maxDuration: 30000, // 30 seconds
  silenceTimeout: 3000, // 3 seconds
  silenceThreshold: 0.01, // Volume threshold for silence detection
};

export const useAudioRecorder = (): UseAudioRecorderReturn => {
  const [state, setState] = useState<AudioRecorderState>({
    isRecording: false,
    isProcessing: false,
    audioBlob: null,
    duration: 0,
    error: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const durationTimerRef = useRef<NodeJS.Timeout | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Check if audio recording is supported
  const isSupported = Boolean(
    navigator.mediaDevices &&
    navigator.mediaDevices.getUserMedia &&
    window.MediaRecorder
  );

  // Cleanup function
  const cleanup = useCallback(() => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (durationTimerRef.current) {
      clearInterval(durationTimerRef.current);
      durationTimerRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
    mediaRecorderRef.current = null;
  }, []);

  // Silence detection
  const detectSilence = useCallback(() => {
    if (!analyserRef.current) return;

    const bufferLength = analyserRef.current.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate average volume
    const average = dataArray.reduce((sum, value) => sum + value, 0) / bufferLength;
    const normalizedVolume = average / 255;

    // Check if volume is below silence threshold
    if (normalizedVolume < DEFAULT_CONFIG.silenceThreshold) {
      if (!silenceTimerRef.current) {
        silenceTimerRef.current = setTimeout(() => {
          console.log('Silence detected, stopping recording');
          stopRecording();
        }, DEFAULT_CONFIG.silenceTimeout);
      }
    } else {
      // Reset silence timer if sound is detected
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
    }

    // Continue monitoring
    animationFrameRef.current = requestAnimationFrame(detectSilence);
  }, []);

  // Start recording
  const startRecording = useCallback(async (): Promise<void> => {
    if (!isSupported) {
      setState(prev => ({ ...prev, error: 'Audio recording not supported' }));
      return;
    }

    try {
      setState(prev => ({ ...prev, isProcessing: true, error: null }));

      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: DEFAULT_CONFIG.sampleRate,
          channelCount: DEFAULT_CONFIG.channels,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Set up audio context for silence detection
      audioContextRef.current = new AudioContext();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);

      // Set up MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setState(prev => ({
          ...prev,
          isRecording: false,
          isProcessing: false,
          audioBlob,
        }));
        cleanup();
      };

      mediaRecorder.onerror = (event) => {
        console.error('MediaRecorder error:', event);
        setState(prev => ({
          ...prev,
          isRecording: false,
          isProcessing: false,
          error: 'Recording failed',
        }));
        cleanup();
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms

      // Start duration timer
      let duration = 0;
      durationTimerRef.current = setInterval(() => {
        duration += 100;
        setState(prev => ({ ...prev, duration }));

        // Stop if max duration reached
        if (duration >= DEFAULT_CONFIG.maxDuration) {
          stopRecording();
        }
      }, 100);

      // Start silence detection
      detectSilence();

      setState(prev => ({
        ...prev,
        isRecording: true,
        isProcessing: false,
        duration: 0,
      }));

      console.log('Recording started');
    } catch (error) {
      console.error('Failed to start recording:', error);
      setState(prev => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        error: error instanceof Error ? error.message : 'Failed to start recording',
      }));
      cleanup();
    }
  }, [isSupported, detectSilence, cleanup]);

  // Stop recording
  const stopRecording = useCallback(async (): Promise<Blob | null> => {
    if (!mediaRecorderRef.current || !state.isRecording) {
      return null;
    }

    try {
      setState(prev => ({ ...prev, isProcessing: true }));

      mediaRecorderRef.current.stop();
      console.log('Recording stopped');

      // Return the audio blob (will be set in the onstop handler)
      return new Promise((resolve) => {
        const checkForBlob = () => {
          if (state.audioBlob) {
            resolve(state.audioBlob);
          } else {
            setTimeout(checkForBlob, 100);
          }
        };
        checkForBlob();
      });
    } catch (error) {
      console.error('Failed to stop recording:', error);
      setState(prev => ({
        ...prev,
        isRecording: false,
        isProcessing: false,
        error: 'Failed to stop recording',
      }));
      cleanup();
      return null;
    }
  }, [state.isRecording, state.audioBlob, cleanup]);

  // Clear recording
  const clearRecording = useCallback(() => {
    setState(prev => ({
      ...prev,
      audioBlob: null,
      duration: 0,
      error: null,
    }));
    audioChunksRef.current = [];
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return {
    state,
    startRecording,
    stopRecording,
    clearRecording,
    isSupported,
  };
};

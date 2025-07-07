/**
 * EVA-Dev Frontend Application
 * Main application component
 */

import React from 'react';
import styled, { createGlobalStyle, ThemeProvider } from 'styled-components';
import ChatWidget from './components/ChatWidget';

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f8fafc;
    color: #1e293b;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }

  /* Scrollbar styles */
  ::-webkit-scrollbar {
    width: 6px;
  }

  ::-webkit-scrollbar-track {
    background: #f1f5f9;
  }

  ::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
`;

// Theme configuration
const theme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    success: '#10b981',
    gray: {
      50: '#f8fafc',
      100: '#f1f5f9',
      200: '#e2e8f0',
      300: '#cbd5e1',
      400: '#94a3b8',
      500: '#64748b',
      600: '#475569',
      700: '#334155',
      800: '#1e293b',
      900: '#0f172a',
    },
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px',
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '50%',
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppContainer>
        <Header>
          <Logo>
            <h1>EVA-Dev Demo</h1>
            <p>Voice-Enabled EV Charging Support AI</p>
          </Logo>
          <StatusIndicator>
            <StatusDot />
            <span>Live Demo</span>
          </StatusIndicator>
        </Header>

        <MainContent>
          <WelcomeSection>
            <WelcomeCard>
              <h2>🚗⚡ Welcome to EVA-Dev</h2>
              <p>
                Your intelligent EV charging assistant is ready to help! EVA-Dev specializes in:
              </p>
              <FeatureList>
                <li>🔌 Charging station troubleshooting</li>
                <li>🔧 Connector type guidance (Type 1, Type 2, CCS, CHAdeMO)</li>
                <li>⚡ Charging speed optimization</li>
                <li>🏠 Home charging setup advice</li>
                <li>💰 Cost-effective charging strategies</li>
                <li>🗺️ Charging network information</li>
              </FeatureList>
              <CallToAction>
                <strong>Try it now!</strong> Click the chat button in the bottom-right corner to start a conversation, 
                or use the voice button to speak with EVA-Dev directly.
              </CallToAction>
            </WelcomeCard>

            <DemoFeatures>
              <FeatureCard>
                <h3>💬 Text Chat</h3>
                <p>Type your EV charging questions and get instant, expert responses.</p>
              </FeatureCard>
              <FeatureCard>
                <h3>🎤 Voice Interaction</h3>
                <p>Speak naturally - EVA-Dev will listen, understand, and respond with voice.</p>
              </FeatureCard>
              <FeatureCard>
                <h3>🧠 AI-Powered</h3>
                <p>Powered by Claude AI with specialized knowledge in EV charging technology.</p>
              </FeatureCard>
            </DemoFeatures>
          </WelcomeSection>
        </MainContent>

        <Footer>
          <p>
            Built with ❤️ using React, TypeScript, FastAPI, Azure Speech Services, and Claude AI
          </p>
          <TechStack>
            <TechBadge>React</TechBadge>
            <TechBadge>TypeScript</TechBadge>
            <TechBadge>FastAPI</TechBadge>
            <TechBadge>Azure Speech</TechBadge>
            <TechBadge>Claude AI</TechBadge>
            <TechBadge>Docker</TechBadge>
          </TechStack>
        </Footer>

        {/* Chat Widget */}
        <ChatWidget
          showVoiceButton={true}
          theme="light"
          position="bottom-right"
          initialMessage="Hello! I'm EVA-Dev, your EV charging assistant. How can I help you today?"
        />
      </AppContainer>
    </ThemeProvider>
  );
};

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: ${({ theme }) => theme.shadows.md};
`;

const Logo = styled.div`
  h1 {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }

  p {
    font-size: 1.1rem;
    opacity: 0.9;
  }
`;

const StatusIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.9rem;
`;

const StatusDot = styled.div`
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const MainContent = styled.main`
  flex: 1;
  padding: 3rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const WelcomeSection = styled.section`
  display: grid;
  gap: 2rem;
  
  @media (min-width: 768px) {
    grid-template-columns: 2fr 1fr;
  }
`;

const WelcomeCard = styled.div`
  background: white;
  padding: 2rem;
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  box-shadow: ${({ theme }) => theme.shadows.lg};

  h2 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: ${({ theme }) => theme.colors.gray[800]};
  }

  p {
    font-size: 1.1rem;
    line-height: 1.6;
    color: ${({ theme }) => theme.colors.gray[600]};
    margin-bottom: 1.5rem;
  }
`;

const FeatureList = styled.ul`
  list-style: none;
  margin: 1.5rem 0;

  li {
    padding: 0.5rem 0;
    font-size: 1rem;
    color: ${({ theme }) => theme.colors.gray[700]};
  }
`;

const CallToAction = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  margin-top: 1.5rem;
  font-size: 1rem;
  line-height: 1.5;
`;

const DemoFeatures = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const FeatureCard = styled.div`
  background: white;
  padding: 1.5rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  box-shadow: ${({ theme }) => theme.shadows.md};

  h3 {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: ${({ theme }) => theme.colors.gray[800]};
  }

  p {
    font-size: 0.9rem;
    color: ${({ theme }) => theme.colors.gray[600]};
    line-height: 1.4;
  }
`;

const Footer = styled.footer`
  background: ${({ theme }) => theme.colors.gray[800]};
  color: white;
  padding: 2rem;
  text-align: center;

  p {
    margin-bottom: 1rem;
    opacity: 0.9;
  }
`;

const TechStack = styled.div`
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
`;

const TechBadge = styled.span`
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.8rem;
  font-weight: 500;
`;

export default App;

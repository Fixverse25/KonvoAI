name: "KonvoAI: Swedish EV Charging Support System with Voice-Enabled AI Assistant"
description: |

## 📊 Current Status (2025-07-11 23:58 UTC)
**Project Completion**: 95% - Core functionality operational
**Chat System**: ✅ Fully working (Claude integration perfect)
**Voice System**: ⚠️ Azure Speech API subscription issue
**Infrastructure**: ✅ Docker containers stable and healthy
**Frontend**: ✅ Accessible and loading correctly
**Next Priority**: Azure Speech Services troubleshooting

## Purpose
Build and maintain KonvoAI, a production-ready Swedish EV charging support system with voice-enabled conversational AI, GDPR compliance, and Azure Speech Services integration. This system provides intelligent assistance for electric vehicle owners in Sweden through both text and voice interactions.

## Core Principles
1. **Swedish First**: All user-facing content prioritizes Swedish language and market
2. **GDPR by Design**: Privacy compliance built into every component
3. **Voice-Enabled**: Seamless speech-to-text and text-to-speech functionality
4. **EV Expertise**: Deep knowledge of electric vehicle charging technology
5. **Production Ready**: Containerized, scalable, and deployment-ready architecture

---

## Goal
Maintain and enhance a production-ready Swedish EV charging support system that provides intelligent conversational assistance through both text chat and voice interactions, with full GDPR compliance and Azure Speech Services integration.

## Why
- **Market Need**: Swedish EV owners need localized charging support in their native language
- **Accessibility**: Voice interaction makes EV support accessible to more users
- **Compliance**: GDPR compliance ensures legal operation in EU market
- **Technical Excellence**: Demonstrates advanced AI integration patterns with speech services

## What
A comprehensive EV charging support system featuring:
- Swedish-optimized chat widget with voice capabilities
- FastAPI backend with Claude AI integration
- Azure Speech Services for Swedish STT/TTS
- Redis session management with GDPR compliance
- Docker containerization for production deployment

### Success Criteria
- [x] **Development Environment Deployed** (2025-07-08)
  - Backend API running on localhost:8000
  - Frontend serving on localhost:3000
  - Redis cache operational
  - All services communicating successfully
- [x] **Core Services Operational**
  - Claude AI integration working
  - Azure Speech Services configured for Swedish
  - GDPR compliance service implemented
  - Session management with Redis
- [x] **Continuous Voice Call Mode Implemented** (2025-07-11)
  - Green phone button with twin styling
  - Voice activity detection and silence timeout
  - 3-second debounce for speech segmentation
  - Call status badge with waveform animation
  - Mobile compatibility (Chrome/Safari)
- [x] **Frontend-Backend Integration Completed** (2025-07-11)
  - API routing fixed and working
  - GDPR consent removal completed
  - Session management operational
- [ ] Swedish voice interaction works flawlessly with EV terminology (95% complete)
- [ ] Production deployment on Fixverse.se with HTTPS
- [ ] All tests pass and code meets quality standards

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- file: CLAUDE.md
  why: Core project context and AI behavior rules

- file: PLANNING.md
  why: System architecture and component structure

- file: README.md
  why: Project overview and setup instructions

- file: PROJECT_STATUS.md
  why: Real-time project status, implementation guide, and next priorities

- file: DAILY_LOG_2025-07-08.md
  why: Latest session progress - full system deployment and configuration fixes

- file: backend/app/services/claude_service.py
  why: Claude AI integration patterns and system prompts

- file: backend/app/services/azure_speech_service.py
  why: Swedish speech services integration with EV terminology

- file: backend/app/api/endpoints/chat.py
  why: Chat API patterns with GDPR compliance

- file: backend/app/api/endpoints/voice.py
  why: Voice interaction patterns and audio processing

- file: frontend/public/index.html
  why: Swedish chat widget implementation patterns

- file: docs/API.md
  why: API documentation and usage examples

- url: https://docs.anthropic.com/claude/reference/messages
  why: Claude API reference for chat completions

- url: https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/
  why: Azure Speech Services documentation for Swedish language
```

### 🚀 Current Deployment Status (2025-07-11)
```yaml
Development Environment: FULLY OPERATIONAL
Services:
  backend:
    status: RUNNING
    url: http://localhost:8000
    health: /api/v1/health/ ✅
    voice_endpoints: IMPLEMENTED ✅

  frontend:
    status: RUNNING
    url: http://localhost:3000
    access: Browser accessible ✅
    voice_ui: FULLY IMPLEMENTED ✅

  redis:
    status: RUNNING
    container: redis-eva (Docker)
    connection: Backend connected ✅

Recent Major Accomplishments:
  - ✅ Continuous Voice Call Mode FULLY IMPLEMENTED
  - ✅ Green phone button with twin styling
  - ✅ Voice activity detection with 2s silence timeout
  - ✅ 3-second debounce for speech segmentation
  - ✅ Call status badge with waveform animation
  - ✅ Mobile compatibility (Chrome/Safari)
  - ✅ GDPR consent removal completed
  - ✅ Frontend-backend API routing fixed
  - ✅ WebM audio format support added
  - ✅ Docker audio codec improvements

Current Status: 95% COMPLETE
Remaining: Azure Speech SDK Docker platform initialization (5%)
```

### Current Codebase Structure
```bash
KonvoAI/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes & endpoints
│   │   │   └── endpoints/  # Chat, Voice, GDPR endpoints
│   │   ├── core/           # Core configuration
│   │   ├── services/       # Business logic
│   │   │   ├── claude_service.py      # Claude AI integration
│   │   │   ├── azure_speech_service.py # Swedish speech services
│   │   │   ├── gdpr_service.py        # GDPR compliance
│   │   │   └── redis_service.py       # Session management
│   │   └── models/         # Data models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Static HTML/CSS/JS frontend
│   ├── public/
│   │   ├── index.html      # Swedish chat widget
│   │   ├── style.css       # Swedish-optimized styling
│   │   └── script.js       # Voice and chat functionality
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                   # Documentation
│   ├── API.md             # API documentation
│   ├── DEPLOYMENT.md      # Deployment guide
│   └── DEVELOPMENT.md     # Development setup
├── tests/                 # Test suites
│   ├── integration/       # Integration tests
│   └── unit/             # Unit tests
├── docker-compose.yml     # Development environment
├── docker-compose.prod.yml # Production environment
├── CLAUDE.md             # This PRP file
├── PLANNING.md           # Architecture documentation
└── README.md             # Project overview
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Azure Speech Services requires specific audio format for Swedish
# CRITICAL: Claude API has rate limits - monitor usage for production
# CRITICAL: Redis sessions must expire for GDPR compliance (7 days max)
# CRITICAL: All user data must stay in EU/Sweden for GDPR compliance
# CRITICAL: Swedish EV terminology must be consistent across all interfaces
# CRITICAL: Voice recognition needs EV-specific phrase lists for accuracy
# CRITICAL: HTTPS required for microphone access in browsers
# CRITICAL: WebSocket connections need proper error handling for voice streams
# CRITICAL: Session management must handle concurrent voice/text interactions
# CRITICAL: Always validate Swedish text encoding (UTF-8) in all components
```

## Implementation Blueprint

### Data Models and Structure

```python
# models/chat.py - Core conversation structures
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_id: str = Field(..., description="Unique message identifier")
    type: Literal["text", "voice"] = "text"
    language: str = Field("sv-SE", description="Message language code")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    language: str = Field("sv-SE", description="Preferred response language")

class VoiceRequest(BaseModel):
    session_id: Optional[str] = None
    language: str = Field("sv-SE", description="Speech recognition language")
    voice_name: str = Field("sv-SE-SofiaNeural", description="TTS voice")

class GDPRDataSubject(BaseModel):
    session_id: str = Field(..., description="Pseudonymized session identifier")
    consent: bool = Field(True, description="User consent status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    data_retention_days: int = Field(7, description="Data retention period")
```

### List of Tasks for Enhancement

```yaml
Task 1: Voice Interaction Improvements
ENHANCE backend/app/services/azure_speech_service.py:
  - PATTERN: Follow existing Swedish EV phrase list patterns
  - Add more EV terminology for better recognition accuracy
  - Implement voice activity detection for better UX
  - Add support for multiple Swedish dialects

Task 2: GDPR Compliance Enhancements
ENHANCE backend/app/services/gdpr_service.py:
  - PATTERN: Follow existing data subject creation patterns
  - Implement automated data deletion after retention period
  - Add user data export functionality (Right to Portability)
  - Create GDPR audit logging system

Task 3: Swedish Language Optimization
ENHANCE frontend/public/index.html:
  - PATTERN: Follow existing Swedish UI patterns
  - Improve Swedish error messages and user feedback
  - Add Swedish keyboard shortcuts for accessibility
  - Optimize Swedish text rendering and typography

Task 4: Claude AI Swedish Expertise
ENHANCE backend/app/services/claude_service.py:
  - PATTERN: Follow existing system prompt patterns
  - Expand Swedish EV market knowledge base
  - Add Swedish charging network specific information
  - Improve Swedish conversational patterns

Task 5: Production Monitoring
CREATE monitoring/:
  - PATTERN: Follow existing Docker patterns
  - Swedish-specific performance metrics
  - GDPR compliance monitoring
  - Voice interaction quality metrics

Task 6: Advanced Voice Features
ENHANCE backend/app/api/endpoints/voice.py:
  - PATTERN: Follow existing voice processing patterns
  - Add voice emotion detection for better UX
  - Implement voice conversation memory
  - Add Swedish accent adaptation
```

### Per Task Pseudocode

```python
# Task 1: Voice Interaction Improvements
async def enhance_swedish_voice_recognition():
    # PATTERN: Extend existing EV phrase list in azure_speech_service.py
    extended_ev_phrases = [
        # Existing phrases plus:
        "laddningsfel", "laddningsavbrott", "kontaktfel",
        "betalningsproblem", "autentiseringsproblem",
        "nödladdning", "reservladdning", "laddningsstatus"
    ]

    # GOTCHA: Azure Speech needs phrase list updates before recognition
    phrase_list_grammar = speechsdk.PhraseListGrammar.from_recognizer(recognizer)
    for phrase in extended_ev_phrases:
        phrase_list_grammar.addPhrase(phrase)

    # PATTERN: Voice activity detection like existing audio processing
    def detect_voice_activity(audio_stream):
        # Implement VAD to improve user experience
        return is_speech_detected

# Task 2: GDPR Compliance Enhancements
async def implement_automated_data_deletion():
    # PATTERN: Follow existing Redis session management
    async def cleanup_expired_sessions():
        current_time = datetime.utcnow()
        for session_id in await redis_service.get_all_sessions():
            session_data = await redis_service.get(f"session:{session_id}")
            if session_data and session_data.get("created_at"):
                created_at = datetime.fromisoformat(session_data["created_at"])
                if (current_time - created_at).days > 7:  # GDPR retention limit
                    await redis_service.delete(f"session:{session_id}")
                    await redis_service.delete(f"conversation:{session_id}")
                    logger.info(f"GDPR: Deleted expired session {session_id}")

# Task 4: Claude AI Swedish Expertise
def enhance_swedish_system_prompt():
    # PATTERN: Extend existing system prompt in claude_service.py
    enhanced_prompt = """
    Du är EVA-Dev, en specialiserad AI-assistent för elbilsladdning i Sverige.

    SVENSKA LADDNÄTVERK:
    - Ionity: Europeiskt snabbladdningsnätverk
    - Vattenfall InCharge: Sveriges största laddnätverk
    - Fortum Charge & Drive: Nordiskt laddnätverk
    - CLEVER: Dansk-svenskt laddnätverk

    SVENSKA REGLERINGAR:
    - Elcertifikat för förnybar energi
    - Skattereduktion för hemmaladdning
    - Miljöbilspremie för elbilar
    """
    return enhanced_prompt
```

### Integration Points
```yaml
ENVIRONMENT:
  - add to: .env
  - vars: |
      # Claude AI Configuration
      ANTHROPIC_API_KEY=your_anthropic_api_key
      CLAUDE_MODEL=claude-3-5-sonnet-20241022
      CLAUDE_MAX_TOKENS=8000

      # Azure Speech Services
      AZURE_SPEECH_KEY=your_azure_speech_key
      AZURE_SPEECH_REGION=swedencentral
      AZURE_SPEECH_LANGUAGE=sv-SE
      AZURE_SPEECH_VOICE=sv-SE-SofiaNeural

      # Redis Configuration
      REDIS_URL=redis://localhost:6379
      REDIS_PASSWORD=your_redis_password

      # GDPR Compliance
      DATA_RETENTION_DAYS=7
      GDPR_CONTACT_EMAIL=privacy@fixverse.se

CONFIG:
  - Swedish Language: Primary interface language (sv-SE)
  - GDPR Compliance: 7-day data retention, EU data residency
  - Voice Integration: Azure Speech Services with EV terminology

DEPENDENCIES:
  - Update requirements.txt with:
    - anthropic>=0.7.0
    - azure-cognitiveservices-speech>=1.24.0
    - fastapi>=0.104.0
    - redis>=4.5.0
    - pydantic>=2.0.0
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd backend
python -m pytest tests/ --verbose                    # Run all tests
python -m flake8 app/ --max-line-length=100         # Style checking
python -m mypy app/ --ignore-missing-imports        # Type checking

# Expected: No errors. If errors, READ and fix.
```

### Level 2: Swedish Language & GDPR Tests
```python
# test_swedish_integration.py
async def test_swedish_voice_recognition():
    """Test Swedish EV terminology recognition"""
    service = AzureSpeechService()
    test_phrases = [
        "Jag behöver hjälp med laddstationen",
        "Min elbil laddar inte",
        "Var finns närmaste snabbladdare?"
    ]

    for phrase in test_phrases:
        # Convert text to speech and back to test recognition
        audio = await service.text_to_speech(phrase)
        recognized = await service.speech_to_text(audio)
        assert phrase.lower() in recognized.lower()

async def test_gdpr_data_retention():
    """Test GDPR compliance with data retention"""
    gdpr_service = GDPRService()
    session_id = "test-session-123"

    # Create data subject
    gdpr_service.create_data_subject(session_id, consent=True)

    # Simulate 8 days passing (beyond 7-day retention)
    with freeze_time(datetime.utcnow() + timedelta(days=8)):
        await gdpr_service.cleanup_expired_data()

    # Verify data is deleted
    assert not await redis_service.get(f"session:{session_id}")

def test_swedish_claude_responses():
    """Test Claude responds in Swedish for EV queries"""
    service = ClaudeService()
    response = await service.chat_completion([
        {"role": "user", "content": "Hur fungerar CCS-laddning?"}
    ])

    # Should respond in Swedish
    assert any(word in response.lower() for word in ["laddning", "elbil", "snabb"])
    assert response  # Should not be empty
```

```bash
# Run Swedish-specific tests:
python -m pytest tests/test_swedish_integration.py -v
python -m pytest tests/test_gdpr_compliance.py -v

# If failing: Debug specific test, fix code, re-run
```

### Level 3: Production Integration Test
```bash
# Test full system with Swedish voice interaction
docker-compose up -d

# Test voice endpoint with Swedish audio
curl -X POST "http://localhost:8000/api/v1/voice/speech-to-text" \
  -H "Content-Type: multipart/form-data" \
  -F "audio_file=@test_swedish_audio.wav"

# Expected response:
# {"transcription": "Jag behöver hjälp med laddstationen", "language": "sv-SE"}

# Test chat endpoint with Swedish text
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Var finns närmaste laddstation?", "session_id": "test"}'

# Expected: Swedish response about charging stations
```

## Final Validation Checklist
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Swedish voice recognition works with EV terms
- [ ] GDPR data retention and deletion working
- [ ] Claude responds in Swedish with EV expertise
- [ ] Frontend chat widget displays Swedish correctly
- [ ] Voice interactions work end-to-end
- [ ] HTTPS deployment ready for production
- [ ] All API endpoints documented in Swedish
- [ ] Error messages display in Swedish
- [ ] Performance acceptable for Swedish users

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode Swedish text - use proper i18n patterns
- ❌ Don't store personal data beyond 7-day GDPR limit
- ❌ Don't use non-EU services for data processing
- ❌ Don't ignore Swedish accessibility standards
- ❌ Don't skip voice testing with actual Swedish audio
- ❌ Don't deploy without HTTPS (required for microphone access)

## Confidence Score: 9/10

High confidence due to:
- Existing production-ready codebase with Swedish integration
- Well-established Azure Speech Services patterns
- Clear GDPR compliance framework already implemented
- Comprehensive test coverage for Swedish functionality

Minor uncertainty on advanced voice features and Swedish dialect variations, but core functionality is solid and well-documented.

---

## 🚀 **MANDATORY: Read These Files Next**

**⚠️ CRITICAL**: After reading this CLAUDE.md file, you MUST immediately read these files in order:

1. **PROJECT_STATUS.md** - Current implementation status and priorities
2. **DAILY_LOG.md** - Recent daily progress and specific changes

**Auto-Action Required**: When prompted to "read CLAUDE.md", automatically also read PROJECT_STATUS.md and DAILY_LOG.md in the same response.

**Optional Context Files** (read if relevant to your task):
- **PLANNING.md** - System architecture and component structure (for architectural questions)
- **docs/API.md** - API documentation and examples (for API integration work)
- **docs/DEVELOPMENT.md** - Development setup and workflow (for environment setup)
- **README.md** - Project overview and setup instructions (for general understanding)

## 🚀 **New Session Checklist for AI Assistants**

When starting work on KonvoAI in a new session, ALWAYS:

1. **Read this file (CLAUDE.md)** - Get project context and behavior rules
2. **IMMEDIATELY read PROJECT_STATUS.md** - Get current implementation status and priorities
3. **Understand the current focus**: Frontend API integration and voice UI implementation
4. **Remember**: System is 80% complete, backend works, frontend needs connection

### **Quick Context Summary:**
- **Project**: Swedish EV charging support with voice-enabled AI
- **Status**: Backend ✅ working, Frontend ⚠️ needs API integration
- **Priority**: Connect chat UI to `/api/v1/chat` endpoint
- **Tech**: FastAPI + Claude + Azure Speech + Redis + Vanilla JS
- **Compliance**: GDPR-first, Swedish language priority

### **Key Development Constraints:**
- **NEVER add API keys to files** - Only in `.env` (gitignored)
- **Swedish language first** - All user-facing content in Swedish
- **GDPR compliance required** - 7-day data retention, EU residency
- **Voice requires HTTPS** - Microphone access needs secure connection
- **No React** - Frontend is vanilla HTML/CSS/JS only

---

## 🧠 AI Behavior Rules for KonvoAI
- **Swedish Priority** - Always default to Swedish language and market knowledge
- **EV Expertise** - Provide accurate, technical EV charging information
- **GDPR Awareness** - Never suggest non-compliant data practices
- **Voice-First Design** - Optimize responses for both text and voice interaction
- **Cultural Adaptation** - Use Swedish communication patterns and terminology
- **Privacy First** - Always consider privacy implications of suggestions
- **Technical Precision** - Accurate information for Swedish EV market and regulations

**Remember**: KonvoAI serves Swedish EV owners with intelligent, privacy-compliant, voice-enabled support. Every decision should prioritize user privacy, Swedish language quality, and EV expertise. 🚗⚡🇸🇪

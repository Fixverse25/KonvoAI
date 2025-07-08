# 📋 KonvoAI - Project Planning & Architecture

## 🎯 Project Overview
**KonvoAI** is a Swedish EV charging support system that provides intelligent, voice-enabled assistance for electric vehicle owners in Sweden. The system combines Claude AI with Azure Speech Services to deliver GDPR-compliant conversational support.

## 🏗️ System Architecture

### 🎨 Frontend (Vanilla HTML/CSS/JS)
```
frontend/
├── public/
│   ├── index.html          # Main Swedish chat interface
│   ├── favicon.ico         # KonvoAI branding
│   └── robots.txt          # SEO optimization
├── serve.py                # Development server with CORS
└── nginx.conf              # Production web server config
```

**Design Principles:**
- Mobile-first responsive design
- Swedish language throughout
- GDPR consent dialog
- Accessibility (WCAG 2.1 AA)
- Progressive enhancement
- Fast loading performance

### 🔧 Backend (FastAPI + Python)
```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py     # Chat conversation endpoints
│   │   │   ├── voice.py    # Speech-to-text/text-to-speech
│   │   │   └── gdpr.py     # Privacy compliance endpoints
│   │   └── routes.py       # API router configuration
│   ├── core/
│   │   ├── config.py       # Environment configuration
│   │   ├── logging.py      # Structured logging
│   │   └── security.py     # Security utilities
│   ├── services/
│   │   ├── claude_service.py      # Claude AI integration
│   │   ├── azure_speech_service.py # Multi-lingual speech services
│   │   ├── gdpr_service.py        # Privacy compliance
│   │   ├── language_service.py    # Language detection and switching
│   │   └── redis_service.py       # Session management
│   └── models/
│       ├── chat.py         # Chat data models
│       ├── voice.py        # Voice data models
│       └── gdpr.py         # Privacy data models
├── requirements.txt        # Python dependencies
└── Dockerfile             # Container configuration
```

### 🗄️ Data Layer
- **Redis**: Session management, conversation history, caching
- **No persistent database**: Privacy by design
- **Data retention**: 7 days conversations, 30 days metadata

### 🔌 External Integrations

#### Claude AI (Anthropic)
- **Model**: claude-3-5-sonnet-20241022
- **Purpose**: Swedish EV charging expertise
- **Configuration**: 8000 max tokens, Swedish context

#### Azure Speech Services
- **Region**: Sweden Central (swedencentral)
- **Language**: sv-SE (Swedish)
- **Voices**: Sofia Neural (primary), Mattias Neural (alternative)
- **Features**: Speech-to-text, text-to-speech, EV terminology

## 🌐 Multi-Lingual Market Focus (Swedish Primary)

### Primary Market: Sweden 🇸🇪
- Swedish EV owners and potential buyers
- Fleet managers in Sweden
- EV charging station operators
- Swedish automotive service providers

### Secondary Markets (Planned Expansion)
- **Norway 🇳🇴**: Norwegian EV market (high EV adoption)
- **Denmark 🇩🇰**: Danish EV market (growing rapidly)
- **International 🌍**: English-speaking EV enthusiasts in Nordic region

### Key Use Cases
1. **Hemmaladdning** - Home charging setup and troubleshooting
2. **Snabbladdning** - Fast charging station location and usage
3. **Laddstationer** - Charging network information and compatibility
4. **Felsökning** - Troubleshooting charging issues
5. **Planering** - Trip planning with charging stops

### Swedish EV Ecosystem
- **Networks**: Ionity, Vattenfall, Fortum, Recharge, Plugsurfing
- **Connectors**: CCS (dominant), CHAdeMO, Type 2, Tesla Supercharger
- **Regulations**: Swedish EV incentives, charging standards
- **Geography**: Urban vs rural charging needs

## 🔒 GDPR Compliance Architecture

### Privacy by Design
- **Data minimization**: Only collect necessary data
- **Purpose limitation**: Data only for EV support
- **Storage limitation**: Automatic deletion after retention period
- **Accuracy**: User can correct their data
- **Security**: Encryption in transit and at rest
- **Accountability**: Audit logs for all data operations

### User Rights Implementation
```
GDPR Endpoints:
├── GET /api/v1/gdpr/privacy-notice    # Privacy policy
├── POST /api/v1/gdpr/consent          # Consent management
├── GET /api/v1/gdpr/export/{session}  # Data portability (Art. 20)
├── DELETE /api/v1/gdpr/data/{session} # Right to deletion (Art. 17)
└── GET /api/v1/gdpr/status/{session}  # Data processing status
```

### Data Categories
1. **Conversation Data**: Chat messages and AI responses
2. **Session Metadata**: Session IDs, timestamps, IP addresses (pseudonymized)
3. **Voice Data**: Temporary audio processing (immediately deleted)
4. **Analytics**: Anonymized usage statistics (optional)

## 🚀 Deployment Architecture

### Development Environment
```yaml
services:
  frontend:    # Nginx serving static files
  backend:     # FastAPI application
  redis:       # Session storage
```

### Production Environment
```yaml
services:
  frontend:    # Nginx with SSL termination
  backend:     # FastAPI with gunicorn
  redis:       # Redis with persistence
  monitoring:  # Health checks and metrics
```

### Infrastructure Requirements
- **Hosting**: Swedish or EU-based hosting (GDPR compliance)
- **SSL/TLS**: HTTPS everywhere
- **Monitoring**: Swedish timezone, privacy-compliant analytics
- **Backup**: Encrypted backups within EU

## 🔧 Development Workflow

### Environment Setup
```bash
# Development
make dev              # Start all services
python3 frontend/serve.py  # Frontend only

# Testing
make test             # All tests
make test-backend     # Backend only
make test-integration # Full system

# Production
make prod             # Production deployment
```

### Code Standards
- **Python**: PEP8, Black formatting, type hints
- **JavaScript**: ES6+, no frameworks, vanilla JS
- **CSS**: Modern CSS, CSS Grid, Flexbox
- **Swedish**: All user-facing text in Swedish
- **GDPR**: Privacy impact assessment for new features

### Testing Strategy
1. **Unit Tests**: Individual service testing
2. **Integration Tests**: API endpoint testing
3. **E2E Tests**: Full user journey testing
4. **Swedish Tests**: Language and cultural testing
5. **GDPR Tests**: Privacy compliance verification

## 📊 Performance Requirements

### Response Times
- **Chat responses**: < 2 seconds
- **Voice processing**: < 1 second
- **Page load**: < 3 seconds
- **API calls**: < 500ms

### Scalability
- **Concurrent users**: 1000+ simultaneous
- **Daily conversations**: 10,000+
- **Voice requests**: 1,000+ per hour
- **Geographic**: Sweden-wide coverage

## 🔍 Monitoring & Analytics

### Key Metrics
- **User satisfaction**: Swedish customer satisfaction scores
- **Response accuracy**: EV knowledge accuracy
- **Performance**: Swedish network performance
- **Privacy compliance**: GDPR audit metrics
- **Usage patterns**: Swedish EV owner behavior

### Privacy-Compliant Analytics
- **No personal data**: Anonymized metrics only
- **Aggregated data**: No individual tracking
- **Opt-in basis**: Users choose analytics participation
- **Transparent reporting**: Clear data usage explanation

## 🎯 Success Criteria

### Technical Success
- [ ] 99.9% uptime for Swedish users
- [ ] < 2 second response times
- [ ] GDPR compliance audit passed
- [ ] Swedish accessibility standards met
- [ ] Mobile-first design validated

### Business Success
- [ ] High Swedish user satisfaction
- [ ] Accurate EV charging guidance
- [ ] Reduced customer support load
- [ ] Positive Swedish market feedback
- [ ] Sustainable operating costs

### User Success
- [ ] Easy EV charging problem resolution
- [ ] Natural Swedish conversation experience
- [ ] Privacy confidence and trust
- [ ] Accessible across devices
- [ ] Valuable EV knowledge gained

---

**Next Steps**: Implement features according to CLAUDE.md rules, focusing on Swedish user experience and GDPR compliance. 🚗⚡🇸🇪

# KonvoAI: AI-Driven EV Charging Support

KonvoAI är en svensk AI-assistent specialiserad på elbilsladdning och support. Systemet erbjuder intelligent textchatt för att hjälpa användare med laddstationer, felsökning och elbilsrelaterade frågor.

## ✨ Funktioner

- 💬 **Intelligent Textchatt**: Realtidskonversation med AI-driven support
- 🗣️ **Svensk Röstfunktion**: Azure Speech Services optimerad för svenska
- 🧠 **Elbilsexpertis**: Specialiserad kunskap inom elbilsladdning med EV-terminologi
- 🔄 **Sessionshantering**: Beständig konversationshistorik med GDPR-compliance
- 🇪🇺 **GDPR-kompatibel**: Fullständig dataskydd med EU-datalagring
- 🐳 **Containeriserad**: Komplett Docker-deployment med produktionsoptimering
- 🔒 **Produktionsklar**: HTTPS, säkerhetsheaders, hastighetsbegränsning
- 📱 **Responsiv**: Fungerar på desktop och mobila enheter
- 🇸🇪 **Svensk**: Fullständigt svenskt gränssnitt och support

## 🏗️ Arkitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  External APIs  │
│ (HTML/CSS/JS)   │◄──►│  (FastAPI/Py)   │◄──►│                 │
│                 │    │                 │    │ • Claude 3.5    │
│ • Chat Widget   │    │ • REST API      │    │   Sonnet        │
│ • Snabbsvar     │    │ • AI Integration│    │ • Azure Speech  │
│ • Responsiv UI  │    │ • Speech STT/TTS│    │   (sv-SE)       │
│ • GDPR Dialog   │    │ • GDPR Service  │    │ • Sweden Central│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Fixverse25/KonvoAI.git
   cd KonvoAI
   ```

2. Copy environment template:
   ```bash
   cp .env.example .env
   ```

3. Configure required environment variables:
   ```bash
   # Anthropic Claude API
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Azure Speech Services (Swedish Optimized)
   AZURE_SPEECH_KEY=your_azure_speech_key
   AZURE_SPEECH_REGION=swedencentral
   AZURE_SPEECH_LANGUAGE=sv-SE
   AZURE_SPEECH_VOICE=sv-SE-SofiaNeural
   AZURE_SPEECH_REGION=your_azure_region

   # Claude API
   ANTHROPIC_API_KEY=your_anthropic_api_key

   # Application Settings
   FRONTEND_URL=https://fixverse.se
   BACKEND_URL=https://api.fixverse.se
   ```

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 🗣️ Azure Speech Services (Swedish Optimized)

KonvoAI använder Azure Speech Services för röstfunktionalitet optimerad för svenska användare.

### 🇸🇪 Svensk Konfiguration

**Region & Prestanda:**
- **Region**: `swedencentral` - Lägsta latens för svenska användare
- **Språk**: `sv-SE` (Svenska - Sverige)
- **Röster**: Sofia Neural (kvinna), Mattias Neural (man)

**EV-Terminologi Optimering:**
```
Optimerade svenska EV-termer:
• elbil, laddstation, laddkabel, snabbladdning
• AC/DC-laddning, CCS, CHAdeMO, Type 2
• Tesla, Supercharger, kilowatt (kW), kWh
• batteri, räckvidd, hemmaladdning, laddtid
• offentlig laddning, laddningshastighet
```

**Ljudkvalitet:**
- **Samplingsfrekvens**: 16kHz (optimerad för röst)
- **Format**: MP3-komprimering för effektivitet
- **Kanaler**: Mono (röstoptimerad)
- **Läge**: Konversation med svensk interpunktion

### 🎯 Speech-to-Text (STT)
```python
# Exempel på svensk röstinmatning
"Hur laddar jag min elbil hemma?"
"Var finns närmaste snabbladdare?"
"Vad kostar det att ladda på Ionity?"
```

### 🔊 Text-to-Speech (TTS)
```python
# Svenska AI-svar med naturlig röst
"För hemmaladdning rekommenderar jag en 11 kW laddbox..."
"Närmaste CCS-snabbladdare finns 2 km bort..."
```

### 🔧 API Endpoints
```bash
# Röstfunktioner
POST /api/v1/voice/speech-to-text    # Konvertera tal till text
POST /api/v1/voice/text-to-speech    # Konvertera text till tal
GET  /api/v1/voice/voices            # Tillgängliga svenska röster
```

## 📁 Project Structure

```
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
│   │   ├── robots.txt      # SEO optimization
│   │   └── favicon.ico     # Site icon
│   ├── Dockerfile          # Nginx static serving
│   └── nginx.conf          # Web server config
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── .env.example           # Environment template
├── Makefile               # Development commands
└── docs/                  # Documentation
```

## 🔧 Development Workflow

### Commit Conventions
We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add voice recognition feature
fix: resolve audio capture issue
docs: update API documentation
refactor: improve error handling
test: add unit tests for speech service
```

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/*`: Feature development
- `hotfix/*`: Critical fixes

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📚 API Documentation

Once running, visit:
- Development: http://localhost:8000/docs
- Production: https://api.fixverse.se/docs

## 🇪🇺 GDPR Compliance

KonvoAI är fullständigt GDPR-kompatibel med dataskydd enligt EU-lagstiftning.

### 🔐 Dataskydd
- **Datalagring**: Endast inom EU (Sverige/Sweden Central)
- **Pseudonymisering**: Alla användaridentifierare pseudonymiseras
- **Dataretention**: 7 dagar för konversationer, 30 dagar för metadata
- **Rättigheter**: Tillgång, portabilitet, radering enligt GDPR

### 🛡️ Privacy by Design
```bash
# GDPR API endpoints
GET  /api/v1/gdpr/privacy-notice     # Integritetspolicy
POST /api/v1/gdpr/consent           # Samtycke
GET  /api/v1/gdpr/export/{session}  # Dataexport (Art. 20)
DELETE /api/v1/gdpr/data/{session}  # Radera data (Art. 17)
```

### 📋 Datakategorier
- **Konversationsdata**: Chattmeddelanden och AI-svar
- **Sessionsmetadata**: Sessionsidentifierare och tidsstämplar
- **Användningsanalys**: Anonymiserad statistik (valfritt)

## 🔒 Security

- All communication over HTTPS in production
- API key management via environment variables
- CORS configuration for frontend domain
- Rate limiting on API endpoints
- GDPR-compliant data handling and storage

## 🤝 Contributing

1. Create feature branch from `develop`
2. Make changes following coding standards
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

[Add your license here]

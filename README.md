# KonvoAI: AI-Driven EV Charging Support

KonvoAI är en svensk AI-assistent specialiserad på elbilsladdning och support. Systemet erbjuder intelligent textchatt för att hjälpa användare med laddstationer, felsökning och elbilsrelaterade frågor.

## ✨ Funktioner

- 💬 **Intelligent Textchatt**: Realtidskonversation med AI-driven support
- 🧠 **Elbilsexpertis**: Specialiserad kunskap inom elbilsladdning
- 🔄 **Sessionshantering**: Beständig konversationshistorik
- 🐳 **Containeriserad**: Komplett Docker-deployment med produktionsoptimering
- 🔒 **Produktionsklar**: HTTPS, säkerhetsheaders, hastighetsbegränsning
- 📱 **Responsiv**: Fungerar på desktop och mobila enheter
- 🇸🇪 **Svensk**: Fullständigt svenskt gränssnitt och support

## 🏗️ Arkitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  External APIs  │
│ (HTML/CSS/JS)   │◄──►│  (FastAPI/Py)   │◄──►│                 │
│                 │    │                 │    │ • Claude API    │
│ • Chat Widget   │    │ • REST API      │    │ • Azure Speech  │
│ • Snabbsvar     │    │ • AI Integration│    │   (optional)    │
│ • Responsiv UI  │    │ • Logging       │    └─────────────────┘
└─────────────────┘    └─────────────────┘
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
   # Azure Speech Services
   AZURE_SPEECH_KEY=your_azure_speech_key
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

## 📁 Project Structure

```
KonvoAI/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── services/       # Business logic
│   │   └── models/         # Data models
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── .env.example           # Environment template
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

## 🔒 Security

- All communication over HTTPS in production
- API key management via environment variables
- CORS configuration for frontend domain
- Rate limiting on API endpoints

## 🤝 Contributing

1. Create feature branch from `develop`
2. Make changes following coding standards
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## 📄 License

[Add your license here]

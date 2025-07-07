# EVA-Dev Development Guide

This guide covers setting up a development environment for EVA-Dev and contributing to the project.

## Prerequisites

### Required Software
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Node.js**: 18+ (for local frontend development)
- **Python**: 3.11+ (for local backend development)
- **Git**: Latest version

### Required Services
- **Azure Speech Services**: For speech-to-text and text-to-speech
- **Anthropic Claude API**: For conversational AI

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/eva-dev.git
cd eva-dev
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Start Development Environment
```bash
# Using Make (recommended)
make dev

# Or using Docker Compose directly
docker-compose up -d
```

### 4. Access Services
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Development Environment

### Environment Variables
Create a `.env` file with the following development settings:

```bash
# Development URLs
DEV_FRONTEND_URL=http://localhost:3000
DEV_BACKEND_URL=http://localhost:8000

# Azure Speech Services (required)
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
AZURE_SPEECH_LANGUAGE=en-US
AZURE_SPEECH_VOICE=en-US-AriaNeural

# Anthropic Claude API (required)
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000

# Development settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000
REDIS_URL=redis://redis:6379/0

# Audio settings
MAX_AUDIO_DURATION_SECONDS=30
SILENCE_TIMEOUT_SECONDS=3
AUDIO_SAMPLE_RATE=16000
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Docker Development
The recommended way to develop is using Docker Compose:

```bash
# Start all services
make dev

# View logs
make logs

# Restart services
make restart

# Stop services
make stop

# Clean up
make clean
```

### Local Development

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Project Structure

```
eva-dev/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── core/           # Core configuration and utilities
│   │   ├── models/         # Data models and schemas
│   │   ├── services/       # Business logic services
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API clients and services
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   ├── Dockerfile
│   └── package.json
├── nginx/                  # Nginx configuration
├── scripts/                # Deployment and utility scripts
├── docs/                   # Documentation
├── tests/                  # Integration tests
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml # Production environment
├── docker-compose.test.yml # Testing environment
└── Makefile               # Development commands
```

## Development Workflow

### Git Workflow
We use GitFlow with the following branches:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/***: Feature development branches
- **hotfix/***: Critical bug fixes
- **release/***: Release preparation

### Commit Conventions
We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add voice recognition feature
fix: resolve audio capture issue in Safari
docs: update API documentation
style: format code with prettier
refactor: improve error handling in voice service
test: add unit tests for speech service
chore: update dependencies
```

### Branch Naming
- `feature/voice-recognition-improvements`
- `fix/audio-capture-safari-bug`
- `docs/api-documentation-update`
- `hotfix/critical-security-patch`

## Testing

### Running Tests
```bash
# All tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# Integration tests
make test-integration
```

### Writing Tests

#### Backend Tests (pytest)
```python
# tests/test_voice_service.py
import pytest
from app.services.azure_speech_service import AzureSpeechService

@pytest.mark.asyncio
async def test_speech_to_text():
    service = AzureSpeechService()
    # Test implementation
    assert result is not None
```

#### Frontend Tests (Jest + React Testing Library)
```typescript
// src/components/__tests__/ChatWidget.test.tsx
import { render, screen } from '@testing-library/react';
import ChatWidget from '../ChatWidget';

test('renders chat widget', () => {
  render(<ChatWidget />);
  expect(screen.getByText('EVA-Dev')).toBeInTheDocument();
});
```

### Test Coverage
- Maintain >80% code coverage
- All new features must include tests
- Critical paths require integration tests

## Code Quality

### Linting and Formatting

#### Backend (Python)
```bash
cd backend

# Linting
flake8 app/
mypy app/

# Formatting
black app/
isort app/
```

#### Frontend (TypeScript)
```bash
cd frontend

# Linting
npm run lint

# Formatting
npm run format

# Type checking
npm run type-check
```

### Pre-commit Hooks
Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

## Debugging

### Backend Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Use debugger
import pdb; pdb.set_trace()

# Or use VS Code debugger with launch.json
```

### Frontend Debugging
```bash
# React Developer Tools
# Redux DevTools (if using Redux)
# Browser developer tools

# Debug in VS Code
npm run start
# Attach VS Code debugger to Chrome
```

### Docker Debugging
```bash
# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Inspect container
docker inspect eva-dev-backend
```

## Performance Optimization

### Backend Performance
- Use async/await for I/O operations
- Implement proper caching with Redis
- Optimize database queries
- Monitor with profiling tools

### Frontend Performance
- Use React.memo for expensive components
- Implement code splitting
- Optimize bundle size
- Use service workers for caching

## API Development

### Adding New Endpoints
1. Define Pydantic models in `app/models/`
2. Create endpoint in `app/api/endpoints/`
3. Add route to `app/api/routes.py`
4. Write tests
5. Update API documentation

### Example New Endpoint
```python
# app/api/endpoints/new_feature.py
from fastapi import APIRouter, HTTPException
from app.models.new_feature import NewFeatureRequest, NewFeatureResponse

router = APIRouter()

@router.post("/", response_model=NewFeatureResponse)
async def new_feature(request: NewFeatureRequest):
    # Implementation
    return NewFeatureResponse(result="success")
```

## Frontend Development

### Adding New Components
1. Create component in `src/components/`
2. Add TypeScript types in `src/types/`
3. Write tests in `__tests__/`
4. Update Storybook stories (if using)

### State Management
- Use React hooks for local state
- Context API for global state
- Consider Redux for complex state

### Styling
- Styled Components for component styling
- CSS modules for global styles
- Responsive design principles

## Environment Management

### Development Environments
- **Local**: Your development machine
- **Docker**: Containerized development
- **Staging**: Pre-production testing
- **Production**: Live environment

### Configuration Management
- Use environment variables for configuration
- Never commit secrets to version control
- Use different configs per environment

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Port already in use
docker-compose down
sudo lsof -i :8000
kill -9 <PID>

# Permission issues
sudo chown -R $USER:$USER .
```

#### Backend Issues
```bash
# Module not found
pip install -r requirements.txt

# Database connection issues
docker-compose restart redis
```

#### Frontend Issues
```bash
# Node modules issues
rm -rf node_modules package-lock.json
npm install

# Port issues
export PORT=3001
npm start
```

## Contributing

### Pull Request Process
1. Create feature branch from `develop`
2. Make changes with tests
3. Ensure all tests pass
4. Update documentation
5. Submit pull request
6. Address review feedback
7. Merge after approval

### Code Review Guidelines
- Review for functionality, performance, security
- Check test coverage
- Verify documentation updates
- Ensure code style compliance

### Release Process
1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG.md
4. Test release candidate
5. Merge to `main`
6. Tag release
7. Deploy to production

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Tools
- [VS Code](https://code.visualstudio.com/) - Recommended IDE
- [Postman](https://www.postman.com/) - API testing
- [Redis Commander](https://github.com/joeferner/redis-commander) - Redis GUI

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Slack channel for team communication

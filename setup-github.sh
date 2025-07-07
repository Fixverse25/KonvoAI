#!/bin/bash

# =============================================================================
# KonvoAI GitHub Setup Script
# Connects the EVA-Dev project to GitHub repository
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Setting up KonvoAI GitHub Repository${NC}"

# Check if we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "backend" ]] || [[ ! -d "frontend" ]]; then
    echo -e "${YELLOW}⚠️  Please run this script from the project root directory${NC}"
    exit 1
fi

# Initialize git repository if not already done
if [[ ! -d ".git" ]]; then
    echo -e "${BLUE}📁 Initializing Git repository...${NC}"
    git init
else
    echo -e "${GREEN}✅ Git repository already initialized${NC}"
fi

# Create .gitignore if it doesn't exist
if [[ ! -f ".gitignore" ]]; then
    echo -e "${BLUE}📝 .gitignore already exists${NC}"
else
    echo -e "${GREEN}✅ .gitignore already configured${NC}"
fi

# Add all files
echo -e "${BLUE}📦 Adding all files to Git...${NC}"
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
else
    # Create initial commit
    echo -e "${BLUE}💾 Creating initial commit...${NC}"
    git commit -m "feat: initial KonvoAI (EVA-Dev) implementation

🎯 Voice-Enabled EV Charging Support AI

## Features Implemented:
- 🗣️ Voice interaction with push-to-talk functionality
- 💬 Text chat with streaming responses
- 🧠 Claude AI integration for EV charging expertise
- 🎤 Azure Speech Services for STT/TTS
- 🐳 Complete Docker containerization
- 🔒 Production HTTPS deployment for Fixverse.se
- 📚 Comprehensive documentation and testing

## Architecture:
- Backend: Python FastAPI with async processing
- Frontend: React TypeScript with modern hooks
- Infrastructure: Docker Compose + Nginx + Redis
- CI/CD: GitHub Actions with automated testing
- Deployment: Production-ready scripts and monitoring

## Key Components:
- Voice processing pipeline with silence detection
- Session management and conversation history
- Rate limiting and security features
- Multi-stage Docker builds for optimization
- SSL certificate management
- Automated backup and rollback capabilities

Ready for production deployment on Fixverse.se! 🚀"
fi

# Add GitHub remote
echo -e "${BLUE}🔗 Adding GitHub remote...${NC}"
if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Remote 'origin' already exists. Removing and re-adding...${NC}"
    git remote remove origin
fi

git remote add origin https://github.com/Fixverse25/KonvoAI.git

# Set main branch
echo -e "${BLUE}🌿 Setting up main branch...${NC}"
git branch -M main

# Push to GitHub
echo -e "${BLUE}⬆️  Pushing to GitHub...${NC}"
echo -e "${YELLOW}📝 You'll be prompted for your GitHub credentials${NC}"
git push -u origin main

echo -e "${GREEN}✅ Successfully connected to GitHub!${NC}"
echo ""
echo -e "${BLUE}🎉 KonvoAI Repository Setup Complete!${NC}"
echo ""
echo -e "Repository URL: ${BLUE}https://github.com/Fixverse25/KonvoAI${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. 🔐 Set up GitHub Secrets for CI/CD:"
echo "   - Go to: https://github.com/Fixverse25/KonvoAI/settings/secrets/actions"
echo "   - Add: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, ANTHROPIC_API_KEY"
echo ""
echo "2. 🔧 Enable GitHub Actions:"
echo "   - Go to: https://github.com/Fixverse25/KonvoAI/actions"
echo "   - Enable workflows if prompted"
echo ""
echo "3. 🛡️ Set up branch protection:"
echo "   - Go to: https://github.com/Fixverse25/KonvoAI/settings/branches"
echo "   - Add protection rules for main branch"
echo ""
echo "4. 📖 Review the documentation:"
echo "   - README.md: Project overview"
echo "   - docs/DEPLOYMENT.md: Production deployment"
echo "   - docs/DEVELOPMENT.md: Development setup"
echo "   - docs/API.md: API documentation"

#!/bin/bash
# Deployment Script for M365 RAG System on Hetzner
# This script sets up the complete system on a fresh Hetzner AX52 server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   M365 RAG System Deployment Script   ║${NC}"
echo -e "${BLUE}║     Hetzner AX52 - Ubuntu 24.04       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${YELLOW}📝 This script will:${NC}"
echo "  1. Update system packages"
echo "  2. Configure firewall (UFW)"
echo "  3. Install Docker and Docker Compose"
echo "  4. Set up project directory"
echo "  5. Configure environment variables"
echo "  6. Generate secure passwords"
echo "  7. Start all services"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# ============================================
# PHASE 1: System Updates
# ============================================
echo -e "${GREEN}📦 Phase 1: Updating system packages...${NC}"
apt update && apt upgrade -y
apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    ufw \
    fail2ban \
    unattended-upgrades \
    certbot \
    python3-certbot-nginx \
    openssl

# ============================================
# PHASE 2: Firewall Configuration
# ============================================
echo -e "${GREEN}🔥 Phase 2: Configuring firewall...${NC}"
ufw --force reset
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
echo -e "${GREEN}✅ Firewall configured${NC}"

# ============================================
# PHASE 3: Install Docker
# ============================================
echo -e "${GREEN}🐳 Phase 3: Installing Docker...${NC}"
apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

apt install -y \
    ca-certificates \
    gnupg \
    lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Configure Docker storage
mkdir -p /data/docker
cat > /etc/docker/daemon.json <<EOF
{
  "data-root": "/data/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF

systemctl restart docker
systemctl enable docker
echo -e "${GREEN}✅ Docker installed${NC}"

# ============================================
# PHASE 4: Create Deploy User
# ============================================
echo -e "${GREEN}👤 Phase 4: Creating deploy user...${NC}"
if ! id -u deploy > /dev/null 2>&1; then
    useradd -m -s /bin/bash deploy
    usermod -aG sudo,docker deploy
    echo -e "${GREEN}✅ Deploy user created${NC}"
else
    echo -e "${YELLOW}⚠️  Deploy user already exists${NC}"
fi

# ============================================
# PHASE 5: Project Setup
# ============================================
echo -e "${GREEN}📁 Phase 5: Setting up project directory...${NC}"
PROJECT_DIR="/data/m365-rag"
mkdir -p "$PROJECT_DIR"

# Copy project files (assumes you've uploaded them)
if [ -d "/tmp/m365-rag-deploy" ]; then
    cp -r /tmp/m365-rag-deploy/* "$PROJECT_DIR/"
    echo -e "${GREEN}✅ Project files copied${NC}"
else
    echo -e "${YELLOW}⚠️  No project files found in /tmp/m365-rag-deploy${NC}"
    echo -e "${YELLOW}   Please upload project files and re-run or manually copy them${NC}"
fi

# ============================================
# PHASE 6: Generate Secure Passwords
# ============================================
echo -e "${GREEN}🔐 Phase 6: Generating secure passwords...${NC}"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" <<EOF
# M365 RAG System - Environment Configuration
# Generated on $(date)

# Elasticsearch
ELASTIC_PASSWORD=$(openssl rand -base64 32)

# PostgreSQL
POSTGRES_USER=raguser
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=m365_rag

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$(openssl rand -base64 32)

# OpenAI (FILL THIS IN MANUALLY)
OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE

# Azure AD (FILL THESE IN MANUALLY)
AZURE_CLIENT_ID=YOUR_AZURE_CLIENT_ID
AZURE_CLIENT_SECRET=YOUR_AZURE_CLIENT_SECRET
AZURE_TENANT_ID=YOUR_AZURE_TENANT_ID
M365_USE_DELEGATED_AUTH=true

# Security
JWT_SECRET=$(openssl rand -hex 32)
RAGFLOW_SECRET_KEY=$(openssl rand -hex 32)

# Grafana
GRAFANA_USER=admin
GRAFANA_PASSWORD=$(openssl rand -base64 32)

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
    chmod 600 "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ Environment file created with secure passwords${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Edit $PROJECT_DIR/.env and add your API keys!${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists, skipping generation${NC}"
fi

# Set permissions
chown -R deploy:deploy "$PROJECT_DIR"

# ============================================
# PHASE 7: Start Services
# ============================================
echo -e "${GREEN}🚀 Phase 7: Starting services...${NC}"

# Switch to deploy user and start services
su - deploy -c "cd $PROJECT_DIR && docker compose pull"
su - deploy -c "cd $PROJECT_DIR && docker compose up -d"

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start (60 seconds)...${NC}"
sleep 60

# Check service status
su - deploy -c "cd $PROJECT_DIR && docker compose ps"

# ============================================
# PHASE 8: Configure Backups
# ============================================
echo -e "${GREEN}💾 Phase 8: Configuring automated backups...${NC}"

# Make backup scripts executable
chmod +x "$PROJECT_DIR/scripts/backup.sh"
chmod +x "$PROJECT_DIR/scripts/restore.sh"

# Add backup cron job
(crontab -u deploy -l 2>/dev/null; echo "0 2 * * * $PROJECT_DIR/scripts/backup.sh >> /var/log/m365-rag-backup.log 2>&1") | crontab -u deploy -

echo -e "${GREEN}✅ Automated backups configured (daily at 2 AM)${NC}"

# ============================================
# PHASE 9: Configure Fail2ban
# ============================================
echo -e "${GREEN}🛡️  Phase 9: Configuring fail2ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban
echo -e "${GREEN}✅ Fail2ban configured${NC}"

# ============================================
# DEPLOYMENT COMPLETE
# ============================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Deployment Complete! 🎉            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ All services deployed successfully!${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Edit environment file: vi $PROJECT_DIR/.env"
echo "2. Add your OpenAI API key and Azure AD credentials"
echo "3. Restart services: cd $PROJECT_DIR && docker compose restart"
echo "4. Check service status: cd $PROJECT_DIR && docker compose ps"
echo "5. View logs: cd $PROJECT_DIR && docker compose logs -f"
echo ""
echo -e "${YELLOW}🌐 Access Points:${NC}"
echo "  - RAGFlow UI: http://YOUR_SERVER_IP:9380"
echo "  - API: http://YOUR_SERVER_IP:8000"
echo "  - Grafana: http://YOUR_SERVER_IP:3000"
echo "  - MinIO Console: http://YOUR_SERVER_IP:9001"
echo ""
echo -e "${YELLOW}🔐 Grafana Credentials:${NC}"
echo "  Username: admin"
echo "  Password: (check $PROJECT_DIR/.env for GRAFANA_PASSWORD)"
echo ""
echo -e "${YELLOW}📖 Documentation: $PROJECT_DIR/docs/README.md${NC}"
echo ""


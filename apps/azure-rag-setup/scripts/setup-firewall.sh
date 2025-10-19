#!/bin/bash
# Firewall Setup Script for Azure RAG System
# Configures UFW firewall rules for production deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Firewall Configuration Setup        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

# Install UFW if not already installed
if ! command -v ufw &> /dev/null; then
    echo -e "${YELLOW}📦 Installing UFW firewall...${NC}"
    apt update
    apt install -y ufw
fi

# Reset firewall to default state
echo -e "${YELLOW}🔄 Resetting firewall to default state...${NC}"
ufw --force reset

# Configure default policies
echo -e "${YELLOW}🔧 Setting default firewall policies...${NC}"
ufw default deny incoming
ufw default allow outgoing

# Allow essential services
echo -e "${YELLOW}🔓 Configuring essential service rules...${NC}"

# SSH - Allow from anywhere (consider restricting to specific IPs in production)
ufw allow 22/tcp comment 'SSH'

# HTTP - Allow from anywhere
ufw allow 80/tcp comment 'HTTP'

# HTTPS - Allow from anywhere
ufw allow 443/tcp comment 'HTTPS'

# Flask API port
ufw allow 5001/tcp comment 'Flask API'

# Elasticsearch ports (if needed for direct access)
# ufw allow 9200/tcp comment 'Elasticsearch HTTP'
# ufw allow 9300/tcp comment 'Elasticsearch Transport'

# Docker port range (if needed for direct container access)
# ufw allow 8000:9500/tcp comment 'Docker services'

# Enable firewall
echo -e "${YELLOW}🔥 Enabling firewall...${NC}"
ufw --force enable

# Display status
echo -e "${GREEN}✅ Firewall configuration complete!${NC}"
echo ""
ufw status numbered

echo ""
echo -e "${YELLOW}📝 Firewall Rules Summary:${NC}"
echo "  - SSH (22/tcp):     ALLOWED (Consider restricting to specific IPs)"
echo "  - HTTP (80/tcp):    ALLOWED"
echo "  - HTTPS (443/tcp):  ALLOWED"
echo "  - Flask API (5001/tcp): ALLOWED"
echo ""
echo -e "${YELLOW}💡 Security Recommendations:${NC}"
echo "  1. Restrict SSH access to specific IP addresses:"
echo "     sudo ufw delete allow 22/tcp"
echo "     sudo ufw allow from YOUR_IP_ADDRESS to any port 22"
echo ""
echo -e "${YELLOW}🔄 To modify firewall rules later:${NC}"
echo "  - Add rule:    sudo ufw allow PORT/PROTOCOL"
echo "  - Delete rule: sudo ufw delete allow PORT/PROTOCOL"
echo "  - Check status: sudo ufw status"
echo ""
echo -e "${GREEN}🎉 Firewall is now protecting your Azure RAG System!${NC}"
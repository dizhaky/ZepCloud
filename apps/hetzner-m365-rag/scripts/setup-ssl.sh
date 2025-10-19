#!/bin/bash
# SSL Certificate Setup Script
# Obtains and configures Let's Encrypt SSL certificates

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    SSL Certificate Setup               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root or with sudo${NC}"
    exit 1
fi

# Get domain name
echo -e "${YELLOW}Enter your domain name (e.g., rag.example.com):${NC}"
read -r DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ Domain name is required${NC}"
    exit 1
fi

# Get email for Let's Encrypt
echo -e "${YELLOW}Enter your email address for Let's Encrypt notifications:${NC}"
read -r EMAIL

if [ -z "$EMAIL" ]; then
    echo -e "${RED}❌ Email address is required${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📝 Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Setup cancelled."
    exit 0
fi

# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}📦 Installing certbot...${NC}"
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily (needed for standalone mode)
echo -e "${YELLOW}🛑 Stopping nginx temporarily...${NC}"
cd /data/m365-rag
docker compose stop nginx

# Obtain certificate
echo -e "${YELLOW}🔐 Obtaining SSL certificate from Let's Encrypt...${NC}"
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
    echo "Make sure:"
    echo "1. Domain DNS points to this server"
    echo "2. Port 80 is accessible from the internet"
    echo "3. No other process is using port 80"
    docker compose start nginx
    exit 1
fi

echo -e "${GREEN}✅ Certificate obtained successfully${NC}"

# Copy certificates to nginx config directory
echo -e "${YELLOW}📋 Configuring nginx with SSL...${NC}"

NGINX_SSL_DIR="/data/m365-rag/config/nginx/ssl"
mkdir -p "$NGINX_SSL_DIR"

# Copy certificate files
cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$NGINX_SSL_DIR/"
cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$NGINX_SSL_DIR/"

# Set proper permissions
chmod 644 "$NGINX_SSL_DIR/fullchain.pem"
chmod 600 "$NGINX_SSL_DIR/privkey.pem"
chown -R deploy:deploy "$NGINX_SSL_DIR"

# Update nginx configuration
NGINX_CONF="/data/m365-rag/config/nginx/nginx.conf"

echo -e "${YELLOW}📝 Updating nginx configuration...${NC}"

# Create backup
cp "$NGINX_CONF" "$NGINX_CONF.backup"

# Enable HTTPS server block and update domain
sed -i "s/# server {/server {/g" "$NGINX_CONF"
sed -i "s/#     listen 443/    listen 443/g" "$NGINX_CONF"
sed -i "s/#     server_name your-domain.com/    server_name $DOMAIN/g" "$NGINX_CONF"
sed -i "s|#     ssl_certificate /etc/nginx/ssl/fullchain.pem|    ssl_certificate /etc/nginx/ssl/fullchain.pem|g" "$NGINX_CONF"
sed -i "s|#     ssl_certificate_key /etc/nginx/ssl/privkey.pem|    ssl_certificate_key /etc/nginx/ssl/privkey.pem|g" "$NGINX_CONF"
sed -i "s/#     ssl_protocols/    ssl_protocols/g" "$NGINX_CONF"
sed -i "s/#     ssl_ciphers/    ssl_ciphers/g" "$NGINX_CONF"
sed -i "s/#     ssl_prefer_server_ciphers/    ssl_prefer_server_ciphers/g" "$NGINX_CONF"
sed -i "s/#     # HSTS/    # HSTS/g" "$NGINX_CONF"
sed -i "s/#     add_header Strict-Transport-Security/    add_header Strict-Transport-Security/g" "$NGINX_CONF"
sed -i "s/#     location \/ {/    location \/ {/g" "$NGINX_CONF"
sed -i "s/#         proxy_pass/        proxy_pass/g" "$NGINX_CONF"
sed -i "s/#         proxy_set_header/        proxy_set_header/g" "$NGINX_CONF"
sed -i "s/#     }/    }/g" "$NGINX_CONF"
sed -i "s/# }/}/g" "$NGINX_CONF"

# Enable HTTP to HTTPS redirect
sed -i 's/# return 301 https:\/\/\$host\$request_uri;/return 301 https:\/\/$host$request_uri;/g' "$NGINX_CONF"

echo -e "${GREEN}✅ Nginx configuration updated${NC}"

# Restart nginx with new config
echo -e "${YELLOW}🔄 Restarting nginx with SSL...${NC}"
cd /data/m365-rag
docker compose start nginx
sleep 5

# Test nginx configuration
docker compose exec nginx nginx -t

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    echo "Restoring backup configuration..."
    cp "$NGINX_CONF.backup" "$NGINX_CONF"
    docker compose restart nginx
    exit 1
fi

# Test HTTPS access
echo -e "${YELLOW}🧪 Testing HTTPS access...${NC}"
sleep 5

if curl -sf "https://$DOMAIN/health" > /dev/null; then
    echo -e "${GREEN}✅ HTTPS is working!${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS test failed, but configuration is applied${NC}"
    echo "This might be due to DNS propagation delay"
fi

# Set up auto-renewal
echo -e "${YELLOW}⚙️  Configuring automatic certificate renewal...${NC}"

# Test renewal
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Auto-renewal configured successfully${NC}"
    
    # Add cron job if not exists
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'cp /etc/letsencrypt/live/$DOMAIN/*.pem /data/m365-rag/config/nginx/ssl/ && cd /data/m365-rag && docker compose restart nginx'") | crontab -
        echo -e "${GREEN}✅ Renewal cron job added${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Auto-renewal test failed${NC}"
fi

# Update firewall rules
echo -e "${YELLOW}🔥 Updating firewall rules...${NC}"
ufw allow 443/tcp comment 'HTTPS'
ufw status

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ SSL Setup Complete!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "1. Access your site: https://$DOMAIN"
echo "2. Verify HTTPS is working"
echo "3. Check certificate: https://$DOMAIN (inspect in browser)"
echo ""
echo -e "${YELLOW}🔄 Certificate Auto-Renewal:${NC}"
echo "- Certificates will auto-renew before expiration"
echo "- Renewal happens daily at 3:00 AM"
echo "- Check renewal status: certbot renew --dry-run"
echo ""
echo -e "${YELLOW}📋 SSL Files Location:${NC}"
echo "- Certificates: /etc/letsencrypt/live/$DOMAIN/"
echo "- Nginx config: $NGINX_SSL_DIR/"
echo ""


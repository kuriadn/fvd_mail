#!/bin/bash
# Production Deployment Script for Fayvad Mail
# This script sets up the complete production environment

set -e  # Exit on any error

echo "🚀 Fayvad Mail Production Deployment"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="mail.fayvad.com"
APP_PORT="8005"
STATIC_DIR="/var/www/fayvad_mail/staticfiles"
MEDIA_DIR="/var/www/fayvad_mail/media"

echo -e "${YELLOW}Step 1: Setting up directories...${NC}"
sudo mkdir -p /var/www/fayvad_mail
sudo mkdir -p "$STATIC_DIR"
sudo mkdir -p "$MEDIA_DIR"
sudo chown -R www-data:www-data /var/www/fayvad_mail
sudo chmod -R 755 /var/www/fayvad_mail

echo -e "${YELLOW}Step 2: Copying static files from Docker...${NC}"
# Note: Run these commands after starting your Docker container
echo "Run these commands after starting Docker container:"
echo "docker cp fayvad_mail_web:/app/staticfiles/. $STATIC_DIR/"
echo "docker cp fayvad_mail_web:/app/media/. $MEDIA_DIR/"

echo -e "${YELLOW}Step 3: Installing Nginx configuration...${NC}"
sudo cp nginx-production.conf /etc/nginx/sites-available/$DOMAIN

# Test nginx configuration
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration has errors${NC}"
    exit 1
fi

# Enable site
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
sudo rm -f /etc/nginx/sites-enabled/default

echo -e "${YELLOW}Step 4: Setting up SSL certificates...${NC}"
# Install certbot if not already installed
if ! command -v certbot &> /dev/null; then
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Get SSL certificate
echo "Getting SSL certificate for $DOMAIN..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo -e "${YELLOW}Step 5: Restarting services...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${YELLOW}Step 6: Starting application...${NC}"
# Note: You'll need to start your Docker container here
echo "Start your Docker container:"
echo "cd /path/to/fayvad_mail && docker-compose up -d"

echo -e "${GREEN}🎉 Deployment complete!${GREEN}"
echo ""
echo "Your mail application should now be available at:"
echo "https://$DOMAIN"
echo ""
echo "Health check: https://$DOMAIN/health"
echo ""
echo "Don't forget to:"
echo "1. Copy static files from Docker container"
echo "2. Configure your DNS to point $DOMAIN to this server"
echo "3. Set up monitoring and backups"
echo "4. Configure firewall rules"

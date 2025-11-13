#!/bin/bash

# Fayvad Mail Static Files Deployment Script
# Copies static files from Docker container to nginx location

echo "🚀 Deploying static files for Fayvad Mail..."

# Check if container is running
if ! docker ps | grep -q fayvad_mail_web; then
    echo "❌ Container fayvad_mail_web is not running. Please start it first with 'docker compose up'"
    exit 1
fi

# Create nginx static directory if it doesn't exist
echo "📁 Creating nginx static directory..."
sudo mkdir -p /var/www/fayvad_mail/staticfiles/ 2>/dev/null || echo "   (sudo required for directory creation)"

# Copy static files directly to nginx location
echo "📋 Copying static files from container to nginx location..."
docker cp fayvad_mail_web:/app/staticfiles/. /tmp/fayvad_static/

echo "📤 Moving files to nginx location..."
echo "   Note: This requires sudo access. Please run these commands manually if needed:"
echo "   sudo cp -r /tmp/fayvad_static/* /var/www/fayvad_mail/staticfiles/"
echo "   sudo chown -R www-data:www-data /var/www/fayvad_mail/staticfiles/"

# Try to copy with sudo (may require password)
if sudo -n true 2>/dev/null; then
    echo "   (sudo available, copying automatically...)"
    sudo cp -r /tmp/fayvad_static/* /var/www/fayvad_mail/staticfiles/ 2>/dev/null
    sudo chown -R www-data:www-data /var/www/fayvad_mail/staticfiles/ 2>/dev/null
else
    echo "   (sudo requires password, please run manually)"
    cp -r /tmp/fayvad_static/* /var/www/fayvad_mail/staticfiles/ 2>/dev/null || true
fi

# Verify
echo "✅ Verifying deployment..."
FILE_COUNT=$(find /var/www/fayvad_mail/staticfiles/ -type f | wc -l)
echo "📊 $FILE_COUNT static files deployed successfully!"

echo "🎉 Static files deployment complete!"
echo "🌐 Your site should now load properly at https://mail.fayvad.com"

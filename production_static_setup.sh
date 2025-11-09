#!/bin/bash
# Production Static Files Setup

echo "Setting up production directories..."

# Create production directories
sudo mkdir -p /var/www/fayvad_mail
sudo chown -R www-data:www-data /var/www/fayvad_mail

# Copy static files from Docker volume
# (You'll need to copy from your Docker staticfiles volume)
echo "Copy static files from Docker:"
echo "docker cp fayvad_mail_web:/app/staticfiles/. /var/www/fayvad_mail/staticfiles/"

# Copy media files from Docker volume  
echo "Copy media files from Docker:"
echo "docker cp fayvad_mail_web:/app/media/. /var/www/fayvad_mail/media/"

# Set proper permissions
sudo chown -R www-data:www-data /var/www/fayvad_mail
sudo chmod -R 755 /var/www/fayvad_mail

echo "Production setup complete!"
echo "Directories created:"
echo "  /var/www/fayvad_mail/staticfiles/  (for Nginx static serving)"
echo "  /var/www/fayvad_mail/media/        (for Nginx media serving)"

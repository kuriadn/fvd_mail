#!/bin/bash
# Create Postfix and Dovecot configs for Django database
# Run with: sudo bash postfix_dovecot_django_configs.sh

set -e

DB_NAME="fayvad_mail_db"
DB_USER="fayvad"
DB_PASSWORD="MeMiMo@0207"
DB_HOST="localhost"
MAILDIR_BASE="/var/vmail"

echo "Creating Postfix configs for Django database..."

# Backup existing configs
sudo cp /etc/postfix/virtual_mailboxes.cf /etc/postfix/virtual_mailboxes.cf.modoboa.backup
sudo cp /etc/postfix/virtual_domains.cf /etc/postfix/virtual_domains.cf.modoboa.backup
sudo cp /etc/postfix/virtual_aliases.cf /etc/postfix/virtual_aliases.cf.modoboa.backup

# Create Postfix virtual_mailboxes.cf (Django)
sudo tee /etc/postfix/virtual_mailboxes.cf > /dev/null <<EOF
user = ${DB_USER}
password = ${DB_PASSWORD}
hosts = ${DB_HOST}
dbname = ${DB_NAME}
query = SELECT '${MAILDIR_BASE}/' || d.name || '/' || split_part('%s', '@', 1) || '/' FROM mail_emailaccount e JOIN mail_domain d ON e.domain_id = d.id WHERE e.email = '%s' AND e.is_active = true AND d.enabled = true
EOF

# Create Postfix virtual_domains.cf (Django)
sudo tee /etc/postfix/virtual_domains.cf > /dev/null <<EOF
user = ${DB_USER}
password = ${DB_PASSWORD}
hosts = ${DB_HOST}
dbname = ${DB_NAME}
query = SELECT name FROM mail_domain WHERE name='%s' AND enabled=true
EOF

# Create Postfix virtual_aliases.cf (Django) - empty for now
sudo tee /etc/postfix/virtual_aliases.cf > /dev/null <<EOF
user = ${DB_USER}
password = ${DB_PASSWORD}
hosts = ${DB_HOST}
dbname = ${DB_NAME}
query = SELECT email FROM mail_emailaccount WHERE email='%s' AND is_active=true
EOF

echo "Creating Dovecot configs for Django database..."

# Backup existing Dovecot config
sudo cp /etc/dovecot/dovecot-sql.conf.ext /etc/dovecot/dovecot-sql.conf.ext.modoboa.backup

# Create Dovecot SQL config (Django)
sudo tee /etc/dovecot/dovecot-sql.conf.ext > /dev/null <<EOF
driver = pgsql
connect = host=${DB_HOST} dbname=${DB_NAME} user=${DB_USER} password=${DB_PASSWORD}

# Password query - uses password_hash field (CRYPT format)
password_query = SELECT email as user, password_hash as password FROM mail_emailaccount WHERE email='%u' AND is_active=true AND password_hash IS NOT NULL

# User query  
user_query = SELECT '${MAILDIR_BASE}/' || d.name || '/' || split_part('%u', '@', 1) || '/' as home, 'vmail' as uid, 'vmail' as gid FROM mail_emailaccount e JOIN mail_domain d ON e.domain_id = d.id WHERE e.email = '%u' AND e.is_active = true AND d.enabled = true

# Iterate query
iterate_query = SELECT email as user FROM mail_emailaccount WHERE is_active=true
EOF

# Set permissions
sudo chmod 600 /etc/postfix/virtual_mailboxes.cf
sudo chmod 600 /etc/postfix/virtual_domains.cf
sudo chmod 600 /etc/postfix/virtual_aliases.cf
sudo chmod 600 /etc/dovecot/dovecot-sql.conf.ext
sudo chown root:root /etc/postfix/virtual_*.cf
sudo chown root:dovecot /etc/dovecot/dovecot-sql.conf.ext

echo "✅ Configs created"
echo ""
echo "⚠️  IMPORTANT: Test before reloading services!"
echo "   Test Postfix: sudo postmap -q d.kuria@fayvad.com pgsql:/etc/postfix/virtual_mailboxes.cf"
echo "   Test Dovecot: Check /var/log/dovecot.log after restart"
echo ""
echo "To apply changes:"
echo "   sudo postfix reload"
echo "   sudo systemctl restart dovecot"


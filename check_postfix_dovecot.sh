#!/bin/bash
# Check Postfix and Dovecot configuration for d.kuria@fayvad.com
# Run with: bash check_postfix_dovecot.sh

EMAIL="d.kuria@fayvad.com"
DOMAIN="fayvad.com"
USERNAME="d.kuria"

echo "============================================================"
echo "CHECKING POSTFIX/DOVECOT FOR: $EMAIL"
echo "============================================================"

# Check Postfix virtual mailbox map
echo ""
echo "POSTFIX VIRTUAL MAILBOX MAP:"
echo "----------------------------------------"
if [ -f /etc/postfix/virtual ]; then
    if grep -q "$EMAIL" /etc/postfix/virtual; then
        echo "✅ Found in /etc/postfix/virtual:"
        grep "$EMAIL" /etc/postfix/virtual
    else
        echo "❌ Not found in /etc/postfix/virtual"
    fi
else
    echo "⚠️  File not found: /etc/postfix/virtual"
fi

# Check Postfix virtual domains
echo ""
echo "POSTFIX VIRTUAL DOMAINS:"
echo "----------------------------------------"
if [ -f /etc/postfix/virtual_domains ]; then
    if grep -q "$DOMAIN" /etc/postfix/virtual_domains; then
        echo "✅ Domain found in /etc/postfix/virtual_domains:"
        grep "$DOMAIN" /etc/postfix/virtual_domains
    else
        echo "❌ Domain not found in /etc/postfix/virtual_domains"
    fi
else
    echo "⚠️  File not found: /etc/postfix/virtual_domains"
fi

# Check Dovecot passwd file
echo ""
echo "DOVECOT PASSWD FILE:"
echo "----------------------------------------"
if [ -f /etc/dovecot/passwd ]; then
    if grep -q "$EMAIL" /etc/dovecot/passwd; then
        echo "✅ Found in /etc/dovecot/passwd:"
        grep "$EMAIL" /etc/dovecot/passwd | cut -d: -f1
    else
        echo "❌ Not found in /etc/dovecot/passwd"
    fi
else
    echo "⚠️  File not found: /etc/dovecot/passwd"
fi

# Check mail directory
echo ""
echo "MAIL DIRECTORY:"
echo "----------------------------------------"
MAILDIR="/var/mail/vhosts/$DOMAIN/$USERNAME"
if [ -d "$MAILDIR" ]; then
    echo "✅ Mail directory exists: $MAILDIR"
    ls -ld "$MAILDIR"
    echo "Contents:"
    ls -la "$MAILDIR" | head -10
else
    echo "❌ Mail directory not found: $MAILDIR"
    echo "Checking parent directory:"
    ls -la /var/mail/vhosts/ 2>/dev/null || echo "  /var/mail/vhosts/ does not exist"
fi

# Check system user
echo ""
echo "SYSTEM USER:"
echo "----------------------------------------"
SYSUSER="${EMAIL/@/_}"
SYSUSER="${SYSUSER//./_}"
if id "$SYSUSER" &>/dev/null; then
    echo "✅ System user exists: $SYSUSER"
    id "$SYSUSER"
else
    echo "❌ System user not found: $SYSUSER"
    echo "Checking similar users:"
    getent passwd | grep -i "d.kuria\|dkuria\|fayvad" || echo "  No similar users found"
fi

echo ""
echo "============================================================"
echo "CHECK COMPLETE"
echo "============================================================"


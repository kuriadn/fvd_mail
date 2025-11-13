"""
Custom email backends for Django
"""
import ssl
import smtplib
import socket
import os
import logging
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

logger = logging.getLogger(__name__)


class CustomSMTPBackend(EmailBackend):
    """Custom SMTP backend that skips SSL verification for self-signed certs (development)"""
    
    def __init__(self, host=None, port=None, username=None, password=None, 
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None, 
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        """Initialize backend with hostname resolution"""
        super().__init__(host=host, port=port, username=username, password=password,
                        use_tls=use_tls, fail_silently=fail_silently, use_ssl=use_ssl,
                        timeout=timeout, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile, **kwargs)
        # Resolve hostname early to avoid DNS errors later
        # Always resolve, even if host is None (will use settings fallback)
        self.host = self._resolve_smtp_host()
    
    def _resolve_smtp_host(self):
        """Resolve SMTP host with fallback to IP address if hostname fails"""
        smtp_host = self.host or getattr(settings, 'EMAIL_HOST', 'localhost')
        
        # If already an IP address, use it directly
        try:
            socket.inet_aton(smtp_host)
            return smtp_host
        except socket.error:
            pass
        
        # For host.docker.internal or Docker environment, use IP directly
        if smtp_host == 'host.docker.internal' or os.path.exists('/.dockerenv'):
            return getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
        
        # Try to resolve hostname, fallback to IP if it fails
        try:
            socket.gethostbyname(smtp_host)
            return smtp_host
        except socket.gaierror:
            fallback_ip = getattr(settings, 'MAIL_SERVER_IP', '167.86.95.242')
            logger.warning(f"SMTP host '{smtp_host}' not resolvable, using IP: {fallback_ip}")
            return fallback_ip
    
    def open(self):
        if self.connection:
            return False
        try:
            # Use already-resolved host from __init__
            smtp_host = self.host
            
            self.connection = smtplib.SMTP(smtp_host, self.port, timeout=self.timeout)
            if self.use_tls:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                self.connection.starttls(context=context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except (smtplib.SMTPException, socket.gaierror, OSError) as e:
            if not self.fail_silently:
                logger.error(f"SMTP connection error: {e}")
                raise
            return False


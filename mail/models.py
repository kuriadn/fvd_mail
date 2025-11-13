from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Domain(models.Model):
    """Domain model for email domains"""

    name = models.CharField(max_length=253, unique=True)
    enabled = models.BooleanField(default=True)

    # Domain type
    DOMAIN_TYPE_CHOICES = [
        ('domain', 'Primary Domain'),
        ('relaydomain', 'Relay Domain'),
        ('aliasdomain', 'Alias Domain'),
    ]
    type = models.CharField(
        max_length=20,
        choices=DOMAIN_TYPE_CHOICES,
        default='domain'
    )

    # Quotas and limits
    quota = models.IntegerField(default=0, help_text="Domain quota in MB (0 = unlimited)")
    default_mailbox_quota = models.IntegerField(default=1024, help_text="Default mailbox quota in MB")
    message_limit = models.IntegerField(default=0, help_text="Messages per hour (0 = unlimited)")

    # Security features
    antivirus = models.BooleanField(default=True)
    antispam = models.BooleanField(default=True)
    spam_threshold = models.IntegerField(default=5, help_text="Spam score threshold")

    # Organization
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='domains'
    )

    # Metadata
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Domain')
        verbose_name_plural = _('Domains')
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_users(self):
        return self.organization.users.count()

    @property
    def total_mailboxes(self):
        return self.email_accounts.filter(is_active=True).count()

    @property
    def total_aliases(self):
        # For now, return 0 since we don't have aliases implemented
        return 0


class DomainDKIM(models.Model):
    """DKIM configuration for domains - separated for BCNF compliance"""

    domain = models.OneToOneField(
        Domain,
        on_delete=models.CASCADE,
        related_name='dkim_config'
    )

    enabled = models.BooleanField(default=True)
    selector = models.CharField(max_length=100, default='mail')
    private_key = models.TextField(blank=True, null=True)
    public_key = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _('Domain DKIM')
        verbose_name_plural = _('Domain DKIMs')

    def __str__(self):
        return f"DKIM for {self.domain.name}"


class EmailAccount(models.Model):
    """Email account model"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_accounts')
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='email_accounts')

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Quota and usage
    quota_mb = models.IntegerField(default=1024)  # 1GB default
    usage_mb = models.IntegerField(default=0, editable=False)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Password hash for Dovecot (stored separately from Django user password)
    # Format: CRYPT hash compatible with Dovecot
    password_hash = models.CharField(max_length=255, blank=True, null=True, help_text="Password hash for Dovecot authentication")

    class Meta:
        verbose_name = _('Email Account')
        verbose_name_plural = _('Email Accounts')
        ordering = ['email']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def usage_percentage(self):
        return (self.usage_mb / self.quota_mb * 100) if self.quota_mb > 0 else 0
    
    @property
    def organization(self):
        """Derived from domain.organization (3NF compliance)"""
        return self.domain.organization


class EmailFolder(models.Model):
    """Email folder model"""

    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE, related_name='folders')

    name = models.CharField(max_length=100)  # INBOX, Sent, Drafts, Trash, etc.
    display_name = models.CharField(max_length=100)
    unread_count = models.IntegerField(default=0, editable=False)
    total_count = models.IntegerField(default=0, editable=False)

    # Special folders
    is_special = models.BooleanField(default=False)
    folder_type = models.CharField(
        max_length=20,
        choices=[
            ('inbox', 'Inbox'),
            ('sent', 'Sent'),
            ('drafts', 'Drafts'),
            ('trash', 'Trash'),
            ('spam', 'Spam'),
            ('archive', 'Archive'),
            ('custom', 'Custom'),
        ],
        default='custom'
    )

    class Meta:
        verbose_name = _('Email Folder')
        verbose_name_plural = _('Email Folders')
        unique_together = ['account', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.account.email} - {self.display_name}"

    def update_counts(self):
        """Update unread and total message counts"""
        self.total_count = self.messages.count()
        self.unread_count = self.messages.filter(is_read=False).count()
        self.save(update_fields=['total_count', 'unread_count'])


class EmailMessage(models.Model):
    """Email message model"""

    folder = models.ForeignKey(EmailFolder, on_delete=models.CASCADE, related_name='messages')

    # Message identifiers
    message_id = models.CharField(max_length=255, unique=True, db_index=True)
    uid = models.CharField(max_length=100, blank=True, null=True)

    # Headers
    subject = models.TextField()
    sender = models.EmailField()
    sender_name = models.CharField(max_length=200, blank=True, null=True)
    to_recipients = models.JSONField()  # List of email addresses
    cc_recipients = models.JSONField(default=list)  # List of email addresses
    bcc_recipients = models.JSONField(default=list)  # List of email addresses

    # Content
    body_text = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    snippet = models.TextField(blank=True, null=True) 

    # Metadata
    date_sent = models.DateTimeField(help_text="Date when email was sent (from email header)")
    date_received = models.DateTimeField(help_text="Date when email was received (from email header or server)")
    size_bytes = models.IntegerField(default=0)

    # Status
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Flags
    flags = models.JSONField(default=list)  # ['\\Seen', '\\Flagged', etc.]

    class Meta:
        verbose_name = _('Email Message')
        verbose_name_plural = _('Email Messages')
        ordering = ['-date_received']
        indexes = [
            models.Index(fields=['folder', 'date_received']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.sender}"

    @property
    def from_display(self):
        return self.sender_name or self.sender

    @property
    def has_attachments(self):
        return self.attachments.exists()
    
    @property
    def account(self):
        """Derived from folder.account (3NF compliance)"""
        return self.folder.account


class EmailAttachment(models.Model):
    """Email attachment model"""

    message = models.ForeignKey(EmailMessage, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)

    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.IntegerField()
    attachment_file = models.FileField(upload_to='email_attachments/')

    # For inline attachments (images in HTML)
    content_id = models.CharField(max_length=255, blank=True, null=True)
    is_inline = models.BooleanField(default=False)

    # Temporary storage for uploads before email sending
    is_temporary = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_attachments', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = _('Email Attachment')
        verbose_name_plural = _('Email Attachments')

    def __str__(self):
        return f"{self.filename} ({self.message.subject if self.message else 'Temporary'})"


class Draft(models.Model):
    """Draft email model"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='drafts')

    # Email fields
    to_recipients = models.JSONField(default=list)
    cc_recipients = models.JSONField(default=list)
    bcc_recipients = models.JSONField(default=list)
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Draft')
        verbose_name_plural = _('Drafts')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Draft: {self.subject or 'No subject'} - {self.user.username}"


class EmailTemplate(models.Model):
    """Email templates for business communications"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_templates')

    name = models.CharField(max_length=100)
    subject_template = models.CharField(max_length=255)
    body_template = models.TextField()

    # Template variables (JSON schema)
    variables = models.JSONField(default=dict, help_text="Available template variables")

    # Categorization
    category = models.CharField(max_length=50, choices=[
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('support', 'Support'),
        ('personal', 'Personal'),
    ], default='business')

    is_public = models.BooleanField(default=False)  # Organization-wide templates
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
        unique_together = ['user', 'name']
    
    @property
    def organization(self):
        """Derived from user.organization (3NF compliance)"""
        return self.user.organization if self.user.organization else None

    def __str__(self):
        org_name = self.organization.name if self.organization else "No Organization"
        return f"{org_name}: {self.name}"


class Contact(models.Model):
    """Contact management for CRM"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')

    # Basic info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    # Business info
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)

    # Contact details
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Tagging and categorization
    tags = models.JSONField(default=list)  # ['customer', 'prospect', 'vendor']
    source = models.CharField(max_length=50, choices=[
        ('manual', 'Manual Entry'),
        ('email', 'From Email'),
        ('import', 'Import'),
        ('web_form', 'Web Form'),
    ], default='manual')

    # Status and lifecycle
    is_active = models.BooleanField(default=True)
    last_contacted = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-updated_at']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    
    @property
    def organization(self):
        """Derived from user.organization (3NF compliance)"""
        return self.user.organization if self.user.organization else None


class Task(models.Model):
    """Task management for project collaboration"""

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Status and priority
    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='todo')

    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')

    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Relationships
    parent_task = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks')
    related_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.SET_NULL)

    # Metadata
    tags = models.JSONField(default=list)
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.assigned_to.get_full_name()}"


class Project(models.Model):
    """Project management for business workflows"""

    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='planning')

    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Team
    team_members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projects', blank=True)

    # Budget and tracking
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Progress tracking
    progress_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.organization.name}: {self.name}"


class Document(models.Model):
    """Document management for file storage and sharing"""

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_documents')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # File handling
    file = models.FileField(upload_to='documents/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)

    # Categorization
    category = models.CharField(max_length=50, choices=[
        ('contract', 'Contract'),
        ('invoice', 'Invoice'),
        ('proposal', 'Proposal'),
        ('report', 'Report'),
        ('presentation', 'Presentation'),
        ('other', 'Other'),
    ], default='other')

    # Sharing and permissions
    is_public = models.BooleanField(default=False)  # Organization-wide access
    shared_with = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_documents', blank=True)

    # Version control
    version = models.IntegerField(default=1)
    parent_document = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='versions')

    # Metadata
    tags = models.JSONField(default=list)
    expires_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.file_name})"
    
    @property
    def organization(self):
        """Derived from uploaded_by.organization (3NF compliance)"""
        return self.uploaded_by.organization if self.uploaded_by.organization else None


class EmailSignature(models.Model):
    """Email signatures for professional branding"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_signatures')

    name = models.CharField(max_length=100)
    text_content = models.TextField()
    html_content = models.TextField()

    # Template variables available
    variables = models.JSONField(default=dict)

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Email Signature')
        verbose_name_plural = _('Email Signatures')
        unique_together = ['user', 'name']
    
    @property
    def organization(self):
        """Derived from user.organization (3NF compliance)"""
        return self.user.organization if self.user.organization else None

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.name}"

    def save(self, *args, **kwargs):
        # Ensure only one default signature per user
        if self.is_default:
            EmailSignature.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Notification(models.Model):
    """In-app notifications for user engagement"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')

    title = models.CharField(max_length=200)
    message = models.TextField()

    # Notification type and priority
    notification_type = models.CharField(max_length=50, choices=[
        ('email', 'Email Related'),
        ('task', 'Task Related'),
        ('project', 'Project Related'),
        ('contact', 'Contact Related'),
        ('system', 'System Related'),
    ], default='system')

    priority = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Action URL (for clickable notifications)
    action_url = models.URLField(blank=True)

    # Related objects (optional)
    related_email = models.ForeignKey(EmailMessage, null=True, blank=True, on_delete=models.CASCADE)
    related_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE)
    related_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = models.timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

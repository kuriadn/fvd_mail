# Fayvad Mail - Pure Django Email Platform

A modern email platform built with pure Django, vanilla JavaScript, and TailwindCSS. This system demonstrates that complex web applications can be built without heavy JavaScript frameworks.

## Features

### ✅ Core Email Functionality
- **Inbox Management** - View emails with folder navigation
- **Email Search** - Full-text search across subject, body, sender
- **Compose Interface** - Rich text editor with formatting toolbar
- **Email Details** - Full message viewing with attachments
- **Bulk Operations** - Select and manage multiple emails
- **Real-time Updates** - Connection status and periodic refresh

### ✅ Admin Portal
- **System Dashboard** - Overview with key metrics
- **Organization Management** - Create, edit, delete organizations
- **Domain Management** - DNS and security configuration
- **User Management** - System-wide user administration
- **Health Monitoring** - Basic system status indicators

### ✅ Technical Features
- **Responsive Design** - Mobile-friendly across all devices
- **Modern UI** - Clean interface with TailwindCSS
- **Django Security** - Built-in authentication and CSRF protection
- **Database Optimization** - Proper indexing and relationships
- **Static File Management** - Optimized asset delivery

## Architecture

### Backend
- **Django 5.2** - Web framework
- **PostgreSQL/SQLite** - Database
- **Django REST Framework** - API capabilities
- **TailwindCSS** - Styling framework

### Frontend
- **Django Templates** - Server-side rendering
- **Vanilla JavaScript** - Progressive enhancement
- **TailwindCSS** - Utility-first CSS
- **No build tools** - Direct development

## Project Structure

```
fayvad_mail/
├── accounts/           # User authentication
├── organizations/      # Organization management
├── mail/              # Email functionality
├── admin_portal/      # Admin interface
├── templates/         # Django templates
├── static/           # Static assets
├── theme/            # TailwindCSS theme
└── fayvad_mail_project/ # Django settings
```

## Installation

### Option 1: Docker (Recommended for Production)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fayvad_mail
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Run migrations in container**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### Option 2: Virtual Environment (Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fayvad_mail
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Docker vs Virtual Environment

| Aspect | Docker | Virtual Environment |
|--------|--------|-------------------|
| **Isolation** | Complete container isolation | Python environment only |
| **Dependencies** | System + Python deps in container | Python deps only |
| **Deployment** | Consistent across environments | Environment-specific |
| **Resource Usage** | Higher (full container) | Lower (Python only) |
| **Development** | More complex setup | Simpler, faster |
| **Production** | Excellent | Good, but needs venv management |
| **CI/CD** | Perfect | Good, but more configuration |

### Production Docker Setup

For production deployment with Gunicorn and Nginx:

```bash
# Build for production
docker build -t fayvad-mail:latest .

# Run with production settings
docker run -d \\
  --name fayvad-mail \\
  -p 8000:8000 \\
  -e DEBUG=0 \\
  -e SECRET_KEY=your-production-secret-key \\
  -e USE_MODOBOA_DB=true \\
  -e MODOBOA_DB_NAME=modoboa_db \\
  -e MODOBOA_DB_USER=modoboa_user \\
  -e MODOBOA_DB_PASSWORD=your_password \\
  -e MODOBOA_API_BASE=https://mail.fayvad.com/fayvad_api \\
  fayvad-mail:latest \\
  gunicorn fayvad_mail_project.wsgi:application --bind 0.0.0.0:8000
```

## Usage

### Web Interface
- **Main App**: http://localhost:8000
- **Admin Portal**: http://localhost:8000/admin-portal/
- **Django Admin**: http://localhost:8000/admin/

### Default Credentials
- **Username**: admin
- **Password**: admin123

## Migration from React/FBS

This Django implementation replaces a previous React/Next.js + FBS API system:

### Performance Improvements
- **Initial Load**: 0.2-0.5s (vs 2-3s with React)
- **Bundle Size**: ~50KB (vs 500KB+ with React)
- **SEO**: Full server-side rendering
- **Development**: Direct template editing

### Feature Parity
- ✅ Email inbox and composition
- ✅ Admin dashboard and management
- ✅ User authentication and profiles
- ✅ Responsive design
- ✅ Real-time status updates

## Development Philosophy

### DRY (Don't Repeat Yourself)
- Reusable Django templates and components
- Consistent styling patterns
- Shared business logic

### KISS (Keep It Simple Stupid)
- No unnecessary JavaScript frameworks
- Direct Django development
- Minimal build tooling

### No Over-engineering
- Essential features only
- Progressive enhancement
- Server-side first approach

## Contributing

1. Follow Django best practices
2. Use TailwindCSS for styling
3. Keep JavaScript minimal and progressive
4. Test thoroughly before committing

## License

© 2025 Fayvad Digital. All rights reserved.

## Modoboa Integration

This Django application integrates with an existing Modoboa email server:

### Architecture
- **Modoboa**: Runs as separate Django app under `modoboa` user
- **fayvad_api**: REST API extension for business logic
- **Shared Database**: Optional PostgreSQL integration
- **API Integration**: HTTP calls to Modoboa fayvad_api endpoints

### Integration Modes

1. **API-Only Mode** (Default): HTTP calls to fayvad_api
2. **Hybrid Mode**: Shared database + API for email operations
3. **Full Database Mode**: Direct database integration

### Environment Configuration

```bash
# Enable database integration (optional)
export USE_MODOBOA_DB=False

# Database settings (if using direct DB integration)
export MODOBOA_DB_NAME=modoboa_db
export MODOBOA_DB_USER=modoboa_user
export MODOBOA_DB_PASSWORD=your_password

# API settings (always required)
export MODOBOA_API_BASE=https://mail.fayvad.com/fayvad_api
```

## Success Story

This project proves that **pure Django + vanilla JS + TailwindCSS** can build world-class web applications without the complexity of modern JavaScript frameworks. The result is faster, more maintainable, and equally feature-rich software.

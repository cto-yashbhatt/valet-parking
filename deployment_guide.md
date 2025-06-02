# Deployment Guide - Valet Parking System

## Current Architecture (Integrated)

The system is currently built as an integrated Django application where:
- Django serves both the API and the frontend templates
- Static files (CSS, JS) are served by Django
- Single server handles everything

## Running the Application

### Development
```bash
# Navigate to project directory
cd /home/yash/dezdok/valet-parking

# Activate virtual environment (if using one)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if needed)
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### Production Options

#### Option 1: Single Server with Gunicorn (Recommended)
```bash
# Install production server
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn valet_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

#### Option 2: With Nginx (For better static file serving)
```bash
# Install Nginx
sudo apt install nginx

# Gunicorn with socket
gunicorn valet_project.wsgi:application --bind unix:/tmp/valet_parking.sock --workers 3
```

Nginx configuration (`/etc/nginx/sites-available/valet_parking`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/valet-parking/staticfiles/;
    }

    location /media/ {
        alias /path/to/valet-parking/media/;
    }

    location / {
        proxy_pass http://unix:/tmp/valet_parking.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Alternative: Separate Frontend Architecture

If you want to separate the frontend later, here's how:

### Backend Only (Django API)
```bash
# Remove frontend app from INSTALLED_APPS
# Keep only API endpoints
# Run on port 8000
python manage.py runserver 0.0.0.0:8000
```

### Frontend Options

#### Option A: Static File Server
```bash
# Serve static files with a simple HTTP server
cd static/
python -m http.server 3000
```

#### Option B: Node.js/Express Server
```bash
# Create package.json
npm init -y

# Install dependencies
npm install express

# Create server.js
node server.js  # Runs on port 3000
```

#### Option C: React/Vue/Angular
```bash
# Create React app
npx create-react-app valet-parking-frontend
cd valet-parking-frontend

# Install dependencies
npm install axios bootstrap

# Start development server
npm start  # Runs on port 3000
```

## Docker Deployment

### Single Container (Current Setup)
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "valet_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Multi-Container (If separated)
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

## Environment Variables

Create a `.env` file:
```bash
# Database
DB_NAME=valet_parking
DB_USER=your_user
DB_PASSWORD=your_password

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# WhatsApp/Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

## SSL/HTTPS Setup

### With Certbot (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Basic Logging
```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/valet_parking.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Process Management with Supervisor
```ini
# /etc/supervisor/conf.d/valet_parking.conf
[program:valet_parking]
command=/path/to/venv/bin/gunicorn valet_project.wsgi:application --bind unix:/tmp/valet_parking.sock
directory=/path/to/valet-parking
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/valet_parking.log
```

## Database Setup

### PostgreSQL (Recommended for production)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE valet_parking;
CREATE USER valet_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE valet_parking TO valet_user;
```

### Backup Strategy
```bash
# Backup
pg_dump -U valet_user -h localhost valet_parking > backup.sql

# Restore
psql -U valet_user -h localhost valet_parking < backup.sql
```

## Quick Start Commands

### Development
```bash
# One command to start everything
python manage.py runserver 0.0.0.0:8000
```

### Production
```bash
# Prepare for production
python manage.py collectstatic --noinput
python manage.py migrate

# Start with Gunicorn
gunicorn valet_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --daemon

# Or with systemd service
sudo systemctl start valet_parking
sudo systemctl enable valet_parking
```

## Troubleshooting

### Common Issues
1. **Static files not loading**: Run `python manage.py collectstatic`
2. **Database connection errors**: Check database credentials in `.env`
3. **Permission errors**: Ensure proper file permissions
4. **Port already in use**: Kill existing processes or use different port

### Health Check Endpoint
Add to your Django app:
```python
# In a views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now()})
```

This guide covers all the deployment scenarios you might need!

# Docker Deployment Guide - Valet Parking System

## Quick Start

Deploy your entire valet parking system with one command:

```bash
docker compose up -d
```

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM
- 10GB free disk space

## Setup Instructions

### 1. Clone and Prepare

```bash
# Navigate to your project directory
cd /home/yash/dezdok/valet-parking

# Copy environment file
cp .env.example .env

# Edit environment variables
nano .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your settings:

```bash
# Required: Change these for production
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (default values work for Docker)
DB_NAME=valet_parking
DB_USER=valet_user
DB_PASSWORD=valet_password123

# WhatsApp/Twilio (add your credentials)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886
```

### 3. Deploy

```bash
# Build and start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f web
```

## Services Overview

The deployment includes:

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **nginx**: Reverse proxy (ports 80, 443)

## Access Points

After deployment:

- **Frontend UI**: http://localhost
- **API Documentation**: http://localhost/api/docs/swagger/
- **Django Admin**: http://localhost/admin/
- **Direct API**: http://localhost/api/

## Default Credentials

- **Admin User**: admin / admin123
- **Database**: valet_user / valet_password123

**⚠️ Change these in production!**

## Management Commands

```bash
# View all containers
docker compose ps

# View logs
docker compose logs web
docker compose logs db
docker compose logs nginx

# Execute commands in web container
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser

# Database operations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic

# Restart services
docker compose restart web
docker compose restart nginx

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v
```

## Scaling

Scale the web application:

```bash
# Run 3 web instances
docker compose up -d --scale web=3

# Nginx will automatically load balance
```

## Backup and Restore

### Database Backup

```bash
# Create backup
docker compose exec db pg_dump -U valet_user valet_parking > backup.sql

# Restore backup
docker compose exec -T db psql -U valet_user valet_parking < backup.sql
```

### Full Backup

```bash
# Backup volumes
docker run --rm -v valet-parking_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
docker run --rm -v valet-parking_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup.tar.gz -C /data .
```

## SSL/HTTPS Setup

### 1. Get SSL Certificates

```bash
# Using Let's Encrypt with Certbot
docker run -it --rm \
  -v $(pwd)/nginx/ssl:/etc/letsencrypt \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d your-domain.com
```

### 2. Update Nginx Configuration

Uncomment the HTTPS section in `nginx/default.conf` and update paths:

```nginx
ssl_certificate /etc/nginx/ssl/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/live/your-domain.com/privkey.pem;
```

### 3. Restart Nginx

```bash
docker compose restart nginx
```

## Production Optimizations

### 1. Update Environment Variables

```bash
# In .env file
DEBUG=False
SECRET_KEY=generate-a-strong-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Security headers
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. Resource Limits

Update `docker-compose.yml`:

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### 3. Health Monitoring

```bash
# Check health status
docker compose ps
curl http://localhost/health/

# Monitor resources
docker stats
```

## Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "8080:80"  # Use 8080 instead of 80
   ```

2. **Database connection errors**:
   ```bash
   # Check database logs
   docker compose logs db
   
   # Restart database
   docker compose restart db
   ```

3. **Static files not loading**:
   ```bash
   # Rebuild and collect static files
   docker compose exec web python manage.py collectstatic --noinput
   docker compose restart nginx
   ```

4. **Permission errors**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   ```

### Debug Mode

Enable debug mode temporarily:

```bash
# In .env file
DEBUG=True

# Restart web service
docker compose restart web
```

### Container Shell Access

```bash
# Access web container
docker compose exec web bash

# Access database
docker compose exec db psql -U valet_user valet_parking

# Access nginx
docker compose exec nginx sh
```

## Monitoring and Logs

### Log Locations

- **Application logs**: `./logs/`
- **Nginx logs**: `docker compose logs nginx`
- **Database logs**: `docker compose logs db`

### Log Rotation

Add to `docker-compose.yml`:

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Updates and Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose build web
docker compose up -d web

# Run migrations if needed
docker compose exec web python manage.py migrate
```

### Update Dependencies

```bash
# Update requirements.txt
# Rebuild image
docker compose build --no-cache web
docker compose up -d web
```

## Performance Tuning

### Database Optimization

```bash
# Add to docker-compose.yml db service
environment:
  - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
  - POSTGRES_MAX_CONNECTIONS=100
  - POSTGRES_SHARED_BUFFERS=256MB
```

### Redis Configuration

```bash
# Add to docker-compose.yml redis service
command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set proper ALLOWED_HOSTS
- [ ] Enable security headers
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Update dependencies regularly

## Support

For issues:
1. Check logs: `docker compose logs`
2. Verify configuration: `docker compose config`
3. Test connectivity: `curl http://localhost/health/`
4. Review this guide

Your valet parking system is now ready for production! 🚀

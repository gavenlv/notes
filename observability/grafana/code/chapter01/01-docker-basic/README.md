# Grafana Basic Docker Setup

This is the simplest way to run Grafana using Docker Compose.

## Prerequisites

- Docker installed
- Docker Compose installed

## Quick Start

### 1. Start Grafana

```bash
docker-compose up -d
```

### 2. Access Grafana

Open your browser and navigate to: http://localhost:3000

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### 3. Stop Grafana

```bash
docker-compose down
```

### 4. Stop and Remove Data

```bash
docker-compose down -v
```

## What's Included

- **Grafana**: Latest version running on port 3000
- **Persistent Storage**: Data persists across container restarts
- **Custom Admin Password**: Pre-configured as `admin123`
- **User Signup Disabled**: For security

## Configuration

You can modify the `docker-compose.yml` file to change:

- Admin username/password via `GF_SECURITY_ADMIN_USER` and `GF_SECURITY_ADMIN_PASSWORD`
- Port mapping (change `3000:3000` to `<your-port>:3000`)
- Any other Grafana settings using environment variables

## Environment Variables Format

All Grafana settings can be configured via environment variables:

```
GF_<SECTION>_<KEY>=<value>
```

Examples:
- `GF_SERVER_HTTP_PORT=3000`
- `GF_SECURITY_ADMIN_PASSWORD=mysecret`
- `GF_AUTH_ANONYMOUS_ENABLED=true`

## Useful Commands

```bash
# View logs
docker-compose logs -f grafana

# Restart Grafana
docker-compose restart grafana

# Check status
docker-compose ps

# Execute commands inside container
docker-compose exec grafana bash
```

## Troubleshooting

### Port already in use

If port 3000 is already in use, change it in `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Use port 3001 instead
```

### Reset admin password

```bash
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword
```

### View Grafana version

```bash
docker-compose exec grafana grafana-server -v
```

# Day 1: Installation & Setup

## User Story 1: Install Superset Using Docker

**Title**: As a developer, I want to quickly install Superset using Docker so that I can start learning without complex environment setup.

**Description**: 
Docker provides the fastest way to get Superset running with minimal configuration. This approach is ideal for development and learning purposes.

**Acceptance Criteria**:
- [ ] Superset container starts successfully
- [ ] Web interface is accessible at http://localhost:8088
- [ ] Default admin credentials work
- [ ] Database connection is established
- [ ] All core features are functional

**Step-by-Step Guide**:

1. **Prerequisites Check**
   ```bash
   # Ensure Docker is installed
   docker --version
   docker-compose --version
   ```

2. **Clone Superset Repository**
   ```bash
   git clone https://github.com/apache/superset.git
   cd superset
   ```

3. **Start with Docker Compose**
   ```bash
   # Use the provided docker-compose.yml
   docker-compose up -d
   ```

4. **Initialize Database**
   ```bash
   # Create admin user
   docker-compose exec superset superset fab create-admin \
     --username admin \
     --firstname Superset \
     --lastname Admin \
     --email admin@superset.com \
     --password admin
   
   # Initialize database
   docker-compose exec superset superset db upgrade
   
   # Load examples
   docker-compose exec superset superset load_examples
   
   # Initialize
   docker-compose exec superset superset init
   ```

5. **Access Superset**
   - Open browser: http://localhost:8088
   - Login: admin/admin

**Reference Documents**:
- [Official Docker Installation Guide](https://superset.apache.org/docs/installation/installing-superset-using-docker-compose)
- [Docker Compose Configuration](https://github.com/apache/superset/blob/master/docker-compose.yml)

---

## User Story 2: Install Superset Using pip

**Title**: As a system administrator, I want to install Superset using pip so that I can have full control over the installation and configuration.

**Description**: 
pip installation provides maximum flexibility and control over the Superset environment, suitable for production deployments.

**Acceptance Criteria**:
- [ ] Python virtual environment is created
- [ ] Superset is installed via pip
- [ ] Database is configured and initialized
- [ ] Web server starts successfully
- [ ] Admin user is created

**Step-by-Step Guide**:

1. **Create Virtual Environment**
   ```bash
   python -m venv superset_env
   source superset_env/bin/activate  # On Windows: superset_env\Scripts\activate
   ```

2. **Install Superset**
   ```bash
   pip install apache-superset
   ```

3. **Set Environment Variables**
   ```bash
   export FLASK_APP=superset
   export SUPERSET_HOME=/path/to/superset
   ```

4. **Initialize Database**
   ```bash
   # Initialize the database
   superset db upgrade
   
   # Create admin user
   superset fab create-admin \
     --username admin \
     --firstname Superset \
     --lastname Admin \
     --email admin@superset.com \
     --password admin
   
   # Load examples
   superset load_examples
   
   # Initialize
   superset init
   ```

5. **Start Superset**
   ```bash
   superset run -p 8088 --with-threads --reload --host=0.0.0.0
   ```

**Reference Documents**:
- [Official pip Installation Guide](https://superset.apache.org/docs/installation/installing-superset-from-scratch)
- [Configuration Reference](https://superset.apache.org/docs/installation/configuring-superset)

---

## User Story 3: Install Superset with Custom Database

**Title**: As a production engineer, I want to configure Superset with a production database so that it can handle enterprise workloads.

**Description**: 
Production deployments require robust database backends like PostgreSQL or MySQL for better performance and reliability.

**Acceptance Criteria**:
- [ ] Production database is configured
- [ ] Database connection is tested
- [ ] Superset connects to the database successfully
- [ ] Performance is optimized for production use

**Step-by-Step Guide**:

1. **Install Database Dependencies**
   ```bash
   # For PostgreSQL
   pip install psycopg2-binary
   
   # For MySQL
   pip install mysqlclient
   ```

2. **Configure Database URL**
   ```bash
   # PostgreSQL
   export SQLALCHEMY_DATABASE_URI="postgresql://user:password@localhost:5432/superset"
   
   # MySQL
   export SQLALCHEMY_DATABASE_URI="mysql://user:password@localhost:3306/superset"
   ```

3. **Create Database**
   ```sql
   -- PostgreSQL
   CREATE DATABASE superset;
   CREATE USER superset WITH PASSWORD 'superset';
   GRANT ALL PRIVILEGES ON DATABASE superset TO superset;
   
   -- MySQL
   CREATE DATABASE superset CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'superset'@'localhost' IDENTIFIED BY 'superset';
   GRANT ALL PRIVILEGES ON superset.* TO 'superset'@'localhost';
   FLUSH PRIVILEGES;
   ```

4. **Initialize with Custom Database**
   ```bash
   superset db upgrade
   superset fab create-admin
   superset init
   ```

**Reference Documents**:
- [Database Configuration](https://superset.apache.org/docs/installation/configuring-superset#database)
- [Production Deployment Guide](https://superset.apache.org/docs/installation/running-on-production)

---

## User Story 4: Install Superset with Redis Caching

**Title**: As a performance engineer, I want to configure Redis caching for Superset so that dashboard queries are faster and more responsive.

**Description**: 
Redis caching significantly improves Superset performance by caching query results and session data.

**Acceptance Criteria**:
- [ ] Redis server is installed and running
- [ ] Superset is configured to use Redis
- [ ] Caching is working for dashboard queries
- [ ] Performance improvement is measurable

**Step-by-Step Guide**:

1. **Install Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows
   # Download from https://redis.io/download
   ```

2. **Install Redis Python Client**
   ```bash
   pip install redis
   ```

3. **Configure Superset for Redis**
   ```python
   # In superset_config.py
   CACHE_CONFIG = {
       'CACHE_TYPE': 'redis',
       'CACHE_DEFAULT_TIMEOUT': 300,
       'CACHE_KEY_PREFIX': 'superset_',
       'CACHE_REDIS_HOST': 'localhost',
       'CACHE_REDIS_PORT': 6379,
       'CACHE_REDIS_DB': 1,
       'CACHE_REDIS_URL': 'redis://localhost:6379/1'
   }
   
   # Session configuration
   SESSION_TYPE = 'redis'
   SESSION_REDIS = redis.from_url('redis://localhost:6379/2')
   ```

4. **Test Caching**
   ```bash
   # Test Redis connection
   redis-cli ping
   
   # Restart Superset
   superset run -p 8088
   ```

**Reference Documents**:
- [Caching Configuration](https://superset.apache.org/docs/installation/configuring-superset#caching)
- [Redis Documentation](https://redis.io/documentation)

---

## Troubleshooting Common Issues

### Issue 1: Port Already in Use
```bash
# Check what's using port 8088
lsof -i :8088
# Kill the process or change port
superset run -p 8089
```

### Issue 2: Database Connection Failed
```bash
# Test database connection
python -c "from sqlalchemy import create_engine; engine = create_engine('your_database_url'); engine.connect()"
```

### Issue 3: Permission Denied
```bash
# Fix file permissions
chmod -R 755 /path/to/superset
```

### Issue 4: Memory Issues
```bash
# Increase memory for Docker
docker-compose down
docker system prune
docker-compose up -d
```

## Next Steps

After completing the installation, proceed to:
- [Introduction & Basic Concepts](introduction.md)
- [Configuration & Administration](configuration.md) 
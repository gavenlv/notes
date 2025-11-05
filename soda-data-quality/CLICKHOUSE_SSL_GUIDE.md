# ClickHouse SSL Configuration Guide

## Overview
This guide explains how to configure SSL/TLS encryption for ClickHouse connections in the data quality monitoring system.

## SSL Configuration Options

### Basic SSL Setup
To enable SSL for ClickHouse connections, set the following environment variables:

```bash
# Enable SSL for main ClickHouse connection
CLICKHOUSE_SSL=true

# Enable SSL for ClickHouse DQ (data quality) connection  
CLICKHOUSE_DQ_SSL=true
```

### SSL Verification Options
Control SSL certificate verification:

```bash
# Verify SSL certificates (recommended for production)
CLICKHOUSE_SSL_VERIFY=true
CLICKHOUSE_DQ_SSL_VERIFY=true

# Skip SSL verification (use with caution, for testing only)
CLICKHOUSE_SSL_VERIFY=false
CLICKHOUSE_DQ_SSL_VERIFY=false
```

### SSL Certificate Configuration
For custom SSL certificates, specify the paths:

```bash
# Client certificate (PEM format)
CLICKHOUSE_SSL_CERT=/path/to/client-cert.pem
CLICKHOUSE_SSL_KEY=/path/to/client-key.pem

# Certificate Authority (CA) certificate
CLICKHOUSE_SSL_CA=/path/to/ca-cert.pem

# Same for DQ connection
CLICKHOUSE_DQ_SSL_CERT=/path/to/client-cert.pem
CLICKHOUSE_DQ_SSL_KEY=/path/to/client-key.pem
CLICKHOUSE_DQ_SSL_CA=/path/to/ca-cert.pem
```

## Configuration Examples

### Example 1: Basic SSL (System Certificates)
```bash
# .env file
CLICKHOUSE_SSL=true
CLICKHOUSE_SSL_VERIFY=true
CLICKHOUSE_DQ_SSL=true
CLICKHOUSE_DQ_SSL_VERIFY=true
```

### Example 2: Custom Certificates
```bash
# .env file
CLICKHOUSE_SSL=true
CLICKHOUSE_SSL_VERIFY=true
CLICKHOUSE_SSL_CERT=/etc/ssl/certs/clickhouse-client.crt
CLICKHOUSE_SSL_KEY=/etc/ssl/private/clickhouse-client.key
CLICKHOUSE_SSL_CA=/etc/ssl/certs/ca.crt

CLICKHOUSE_DQ_SSL=true
CLICKHOUSE_DQ_SSL_VERIFY=true
CLICKHOUSE_DQ_SSL_CERT=/etc/ssl/certs/clickhouse-client.crt
CLICKHOUSE_DQ_SSL_KEY=/etc/ssl/private/clickhouse-client.key
CLICKHOUSE_DQ_SSL_CA=/etc/ssl/certs/ca.crt
```

### Example 3: Testing/Development (No Verification)
```bash
# .env file - Use only for development/testing
CLICKHOUSE_SSL=true
CLICKHOUSE_SSL_VERIFY=false
CLICKHOUSE_DQ_SSL=true
CLICKHOUSE_DQ_SSL_VERIFY=false
```

## ClickHouse Server SSL Setup

### Server Configuration (clickhouse-server)
Add to your ClickHouse server configuration:

```xml
<!-- /etc/clickhouse-server/config.d/ssl.xml -->
<clickhouse>
    <https_port>8443</https_port>
    <tcp_port_secure>9440</tcp_port_secure>
    
    <openSSL>
        <server>
            <certificateFile>/etc/clickhouse-server/server.crt</certificateFile>
            <privateKeyFile>/etc/clickhouse-server/server.key</privateKeyFile>
            <dhParamsFile>/etc/clickhouse-server/dhparam.pem</dhParamsFile>
            <verificationMode>none</verificationMode>
            <loadDefaultCAFile>true</loadDefaultCAFile>
            <cacheSessions>true</cacheSessions>
            <disableProtocols>sslv2,sslv3</disableProtocols>
            <preferServerCiphers>true</preferServerCiphers>
        </server>
    </openSSL>
</clickhouse>
```

### Generate Self-Signed Certificates
```bash
# Generate CA
openssl req -x509 -newkey rsa:4096 -keyout ca-key.pem -out ca-cert.pem -days 365 -nodes

# Generate Server Certificate
openssl req -newkey rsa:4096 -keyout server-key.pem -out server-req.pem -days 365 -nodes
openssl x509 -req -in server-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -days 365

# Generate Client Certificate  
openssl req -newkey rsa:4096 -keyout client-key.pem -out client-req.pem -days 365 -nodes
openssl x509 -req -in client-req.pem -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out client-cert.pem -days 365
```

## Testing SSL Connection

### Test SSL Configuration
```bash
# Test with SSL enabled
CLICKHOUSE_SSL=true python -c "
import os
os.environ['CLICKHOUSE_SSL'] = 'true'
from src.core.configuration import EnvironmentConfigurationManager
config = EnvironmentConfigurationManager()
print('SSL Configured Successfully')
"
```

### Test Connection
```bash
# Test ClickHouse connection with SSL
python -c "
import os
from src.core.database_connections import ClickHouseConnection
os.environ['CLICKHOUSE_SSL'] = 'true'
conn = ClickHouseConnection()
# Connection will use SSL if enabled
"
```

## Troubleshooting

### Common Issues

1. **Certificate Verification Failed**
   - Check certificate paths and permissions
   - Ensure CA certificate is valid
   - Set `CLICKHOUSE_SSL_VERIFY=false` for testing

2. **Connection Timeout**
   - Verify ClickHouse SSL port (default: 8443 for HTTPS, 9440 for secure TCP)
   - Check firewall settings
   - Ensure ClickHouse server is configured for SSL

3. **SSL Handshake Error**
   - Verify certificate format (PEM required)
   - Check certificate expiration
   - Ensure client and server certificates match

### Debug SSL Connection
```bash
# Enable debug logging
export CLICKHOUSE_DEBUG=true

# Test with curl
curl -v --cacert ca-cert.pem https://localhost:8443/ping

# Check certificate details
openssl x509 -in client-cert.pem -text -noout
```

## Security Best Practices

1. **Production Environment**
   - Always use certificate verification (`VERIFY=true`)
   - Use proper CA-signed certificates
   - Regularly rotate certificates
   - Monitor certificate expiration

2. **Certificate Management**
   - Store certificates securely
   - Use appropriate file permissions (600 for private keys)
   - Implement automated certificate renewal

3. **Network Security**
   - Use TLS 1.2 or higher
   - Configure strong cipher suites
   - Monitor SSL/TLS connections

## Configuration Reference

### Environment Variables Summary

| Variable | Description | Default |
|----------|-------------|---------|
| `CLICKHOUSE_SSL` | Enable SSL for main connection | `false` |
| `CLICKHOUSE_SSL_VERIFY` | Verify SSL certificates | `true` |
| `CLICKHOUSE_SSL_CERT` | Client certificate path | `None` |
| `CLICKHOUSE_SSL_KEY` | Client private key path | `None` |
| `CLICKHOUSE_SSL_CA` | CA certificate path | `None` |
| `CLICKHOUSE_DQ_SSL` | Enable SSL for DQ connection | `false` |
| `CLICKHOUSE_DQ_SSL_VERIFY` | Verify SSL for DQ connection | `true` |
| `CLICKHOUSE_DQ_SSL_CERT` | DQ client certificate path | `None` |
| `CLICKHOUSE_DQ_SSL_KEY` | DQ client private key path | `None` |
| `CLICKHOUSE_DQ_SSL_CA` | DQ CA certificate path | `None` |

## Next Steps

1. Configure your ClickHouse server for SSL
2. Set up appropriate certificates
3. Update your `.env` file with SSL settings
4. Test the connection
5. Monitor SSL certificate expiration

For additional support, refer to the [ClickHouse SSL documentation](https://clickhouse.com/docs/en/guides/sre/ssl-user-authentication/).
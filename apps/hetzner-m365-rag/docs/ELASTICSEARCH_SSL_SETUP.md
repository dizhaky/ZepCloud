# Elasticsearch SSL/TLS Configuration Guide

## Overview

This guide explains how to set up and manage SSL/TLS encryption for Elasticsearch in the M365 RAG system. SSL/TLS is **enabled by default** for security, encrypting all communication between services and Elasticsearch.

## Why SSL/TLS is Important

Even in internal Docker networks, SSL/TLS provides:

✅ **Encryption in Transit**: Protects credentials and data from network sniffing  
✅ **Authentication**: Verifies identity of Elasticsearch nodes  
✅ **Integrity**: Prevents man-in-the-middle attacks  
✅ **Compliance**: Meets security best practices for production systems  

## Architecture

The SSL configuration includes:

- **HTTP SSL**: Encrypts API communication (client ↔ Elasticsearch)
- **Transport SSL**: Encrypts node-to-node communication (in multi-node setups)
- **Self-Signed Certificates**: Used for internal Docker network communication

## Quick Start

### 1. Generate Certificates (First-Time Setup)

Before starting Elasticsearch for the first time, generate SSL certificates:

```bash
cd /data/m365-rag
chmod +x scripts/generate-es-certs.sh
./scripts/generate-es-certs.sh
```

**Output:**
```
🔐 Generating Elasticsearch SSL Certificates
1️⃣  Generating Certificate Authority (CA)...
✅ CA certificate generated
2️⃣  Generating Elasticsearch private key...
✅ Private key generated
3️⃣  Creating certificate signing request (CSR)...
✅ CSR created
4️⃣  Signing certificate with CA...
✅ Certificate signed
5️⃣  Setting file permissions...
✅ Permissions set
6️⃣  Verifying certificates...
✅ Certificate verification successful

🎉 SSL Certificates Generated Successfully!
```

### 2. Start Elasticsearch

```bash
docker compose up -d elasticsearch
```

### 3. Verify SSL is Working

```bash
# Test HTTPS connection (self-signed cert, so use -k)
curl -k -u elastic:$ELASTIC_PASSWORD https://localhost:9200

# Expected output: Elasticsearch cluster info
```

## Certificate Files

After running `generate-es-certs.sh`, you'll have:

```
config/elasticsearch/certs/
├── ca.crt              # Certificate Authority certificate (public)
├── ca.key              # CA private key (keep secure!)
├── elasticsearch.crt   # Elasticsearch certificate (public)
└── elasticsearch.key   # Elasticsearch private key (keep secure!)
```

### File Permissions

The script automatically sets proper permissions:

- **Public certificates** (`*.crt`): `644` (readable by all)
- **Private keys** (`*.key`): `600` (readable only by owner)

## Configuration Details

### Docker Compose Configuration

The `docker-compose.yml` includes SSL settings:

```yaml
elasticsearch:
  environment:
    # HTTP SSL (API Communication)
    - xpack.security.http.ssl.enabled=true
    - xpack.security.http.ssl.key=/usr/share/elasticsearch/config/certs/elasticsearch.key
    - xpack.security.http.ssl.certificate=/usr/share/elasticsearch/config/certs/elasticsearch.crt
    - xpack.security.http.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca.crt
    - xpack.security.http.ssl.verification_mode=certificate
    
    # Transport SSL (Node-to-Node)
    - xpack.security.transport.ssl.enabled=true
    - xpack.security.transport.ssl.key=/usr/share/elasticsearch/config/certs/elasticsearch.key
    - xpack.security.transport.ssl.certificate=/usr/share/elasticsearch/config/certs/elasticsearch.crt
    - xpack.security.transport.ssl.certificate_authorities=/usr/share/elasticsearch/config/certs/ca.crt
    - xpack.security.transport.ssl.verification_mode=certificate
  
  volumes:
    - ./config/elasticsearch/certs:/usr/share/elasticsearch/config/certs:ro
```

### API Configuration

The API service automatically connects via HTTPS:

```yaml
api:
  environment:
    - ES_USE_SSL=true                    # Enable HTTPS connections
    - ES_VERIFY_CERTS=false              # Accept self-signed certs
```

## Certificate Validity

Certificates are generated with:

- **Validity Period**: 10 years (3650 days)
- **Key Size**: 4096-bit RSA
- **Signature Algorithm**: SHA-256

### Subject Alternative Names (SANs)

Certificates include multiple SANs for flexibility:

- **DNS Names**: `elasticsearch`, `localhost`
- **IP Addresses**: `172.28.0.10` (Docker network), `127.0.0.1`

## Verification Modes

The configuration uses `verification_mode: certificate`:

| Mode | Description | Use Case |
|------|-------------|----------|
| `full` | Verify certificates AND hostnames | Production with proper DNS |
| `certificate` | Verify certificates only | Internal networks, Docker |
| `none` | No verification | ❌ Not recommended |

**We use `certificate`** mode because:
- ✅ Verifies certificate authenticity (signed by CA)
- ✅ Works with Docker internal IPs/hostnames
- ✅ Provides strong security without DNS complexity

## Troubleshooting

### Connection Refused

**Error:** `Failed to establish a new connection`

**Solution:**
1. Check Elasticsearch is running: `docker ps | grep elasticsearch`
2. Check health: `docker compose logs elasticsearch | tail -50`
3. Verify certificates exist: `ls -la config/elasticsearch/certs/`

### SSL Certificate Verification Failed

**Error:** `SSL certificate verification failed`

**Solution:**
1. Regenerate certificates: `./scripts/generate-es-certs.sh`
2. Restart Elasticsearch: `docker compose restart elasticsearch`
3. Check certificate validity:
   ```bash
   openssl x509 -in config/elasticsearch/certs/elasticsearch.crt -noout -dates
   ```

### Certificate Expired

**Error:** `certificate has expired`

**Solution:**
1. Regenerate certificates (they last 10 years): `./scripts/generate-es-certs.sh`
2. Restart services: `docker compose restart elasticsearch api`

### API Can't Connect to Elasticsearch

**Error:** `ConnectionError: HTTPConnectionPool`

**Diagnostic Steps:**
```bash
# 1. Check Elasticsearch SSL is working
curl -k -u elastic:PASSWORD https://localhost:9200

# 2. Check API logs
docker compose logs api | tail -50

# 3. Verify environment variables
docker compose exec api env | grep ES_
```

**Solution:**
Ensure `ES_USE_SSL=true` in API environment variables.

## Security Best Practices

### ✅ DO

- **Generate unique certificates** for each environment (dev/staging/prod)
- **Rotate certificates** every 1-2 years (even though they last 10 years)
- **Restrict file permissions** on private keys (600)
- **Back up certificates** securely (encrypted backup location)
- **Use strong passwords** for Elasticsearch authentication

### ❌ DON'T

- **Commit certificates to git** (they're already .gitignore'd)
- **Share private keys** between environments
- **Disable SSL** unless absolutely necessary for debugging
- **Use the same certificates** for multiple clusters
- **Expose port 9200** to the internet without proper firewall rules

## Advanced: Using Production Certificates

For production with proper domain names and validated certificates:

### Option 1: Let's Encrypt (Recommended)

```bash
# 1. Obtain certificate for your domain
certbot certonly --standalone -d elasticsearch.yourdomain.com

# 2. Copy to config directory
cp /etc/letsencrypt/live/elasticsearch.yourdomain.com/fullchain.pem \
   config/elasticsearch/certs/elasticsearch.crt
cp /etc/letsencrypt/live/elasticsearch.yourdomain.com/privkey.pem \
   config/elasticsearch/certs/elasticsearch.key

# 3. Update verification mode to 'full' in docker-compose.yml
- xpack.security.http.ssl.verification_mode=full

# 4. Update API config
- ES_VERIFY_CERTS=true
```

### Option 2: Corporate CA

```bash
# 1. Get signed certificate from your corporate CA
# 2. Copy certificates to config/elasticsearch/certs/
# 3. Include corporate CA certificate as ca.crt
# 4. Update verification mode to 'full'
# 5. Set ES_VERIFY_CERTS=true in API config
```

## Monitoring

### Check SSL Configuration

```bash
# View certificate details
openssl x509 -in config/elasticsearch/certs/elasticsearch.crt -text -noout

# Check certificate chain
openssl verify -CAfile config/elasticsearch/certs/ca.crt \
  config/elasticsearch/certs/elasticsearch.crt

# Test SSL connection
openssl s_client -connect localhost:9200 \
  -CAfile config/elasticsearch/certs/ca.crt
```

### Elasticsearch Logs

```bash
# Check for SSL-related errors
docker compose logs elasticsearch | grep -i ssl

# Monitor SSL handshake
docker compose logs elasticsearch | grep -i "handshake"
```

## Migration from Non-SSL

If upgrading from a previous non-SSL deployment:

1. **Generate certificates**: `./scripts/generate-es-certs.sh`
2. **Backup data**: `./scripts/backup.sh`
3. **Stop services**: `docker compose down`
4. **Update config**: Already done in new version
5. **Start Elasticsearch**: `docker compose up -d elasticsearch`
6. **Verify SSL**: `curl -k -u elastic:PASSWORD https://localhost:9200`
7. **Start other services**: `docker compose up -d`

## Testing SSL Locally

For local development/testing:

```python
# Python test with requests
import requests

response = requests.get(
    'https://localhost:9200',
    auth=('elastic', 'PASSWORD'),
    verify=False  # For self-signed certs
)
print(response.json())
```

```bash
# Bash test with curl
curl -k -u elastic:PASSWORD https://localhost:9200/_cluster/health?pretty
```

## Performance Impact

SSL/TLS encryption has minimal performance impact:

- **CPU Overhead**: < 5% on modern processors
- **Latency**: < 1ms additional per request
- **Throughput**: No significant impact (hardware acceleration available)

The security benefits **far outweigh** the negligible performance cost.

## Compliance

This SSL configuration helps meet compliance requirements:

- ✅ **PCI DSS**: Encryption in transit
- ✅ **HIPAA**: Data protection requirements
- ✅ **GDPR**: Technical safeguards for data security
- ✅ **SOC 2**: Security controls documentation

## Support

For SSL-related issues:

1. **Check logs**: `docker compose logs elasticsearch api`
2. **Verify certificates**: `openssl verify -CAfile config/elasticsearch/certs/ca.crt config/elasticsearch/certs/elasticsearch.crt`
3. **Test connection**: `curl -k -u elastic:PASSWORD https://localhost:9200`
4. **Review documentation**: This file and `DEPLOYMENT_CHECKLIST.md`

---

**Last Updated:** October 19, 2025  
**Version:** 1.0  
**Status:** Production Ready ✅

**Security Note:** This configuration uses self-signed certificates optimized for internal Docker network communication. For internet-facing deployments, consider using certificates from a trusted Certificate Authority.


# SSL Certificate Configuration for Production Deployment

## Overview

This guide explains how to configure SSL certificates for the M365 RAG System in a production environment. SSL/TLS encryption is essential for securing data in transit between clients and servers.

## Certificate Types

### 1. Self-Signed Certificates (Development/Testing)

For development and testing environments, you can use self-signed certificates:

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:4096 \
    -keyout /etc/ssl/private/selfsigned.key \
    -out /etc/ssl/certs/selfsigned.crt \
    -config /data/m365-rag/config/ssl/openssl.cnf
```

### 2. Let's Encrypt Certificates (Production)

For production environments, we recommend using Let's Encrypt free SSL certificates:

```bash
# Install certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com

# Certificates will be stored in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 3. Commercial Certificates (Enterprise)

For enterprise environments, you can use commercial certificates from trusted Certificate Authorities.

## Nginx SSL Configuration

The nginx configuration already includes SSL settings that are commented out. To enable SSL:

1. Obtain your SSL certificates
2. Update the nginx configuration to uncomment the HTTPS server block
3. Point to your certificate files

Example nginx SSL configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://ragflow;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Certificate Renewal

Let's Encrypt certificates expire every 90 days. Set up automatic renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'" | sudo crontab -
```

## Security Best Practices

1. Use strong encryption (4096-bit RSA keys)
2. Enable HSTS (HTTP Strict Transport Security)
3. Use modern TLS protocols (TLS 1.2 and 1.3)
4. Regularly update certificates before expiration
5. Restrict file permissions on private keys (600)
6. Monitor certificate expiration dates

## Troubleshooting

### Common Issues

1. **Certificate not trusted**: Ensure you're using certificates from a trusted CA
2. **Mixed content warnings**: Ensure all resources are loaded over HTTPS
3. **Certificate mismatch**: Verify the certificate matches your domain name
4. **Expired certificate**: Renew certificates before they expire

### Verification Commands

```bash
# Check certificate details
openssl x509 -in /path/to/certificate.crt -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443

# Verify certificate chain
openssl verify -CAfile /path/to/ca.crt /path/to/certificate.crt
```

## Monitoring

Set up monitoring to ensure SSL certificates remain valid:

```bash
# Check certificate expiration
openssl x509 -in /path/to/certificate.crt -noout -enddate
```

## Backup

Always backup your certificates:

```bash
# Backup Let's Encrypt certificates
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt/
```

This SSL configuration ensures your M365 RAG System is secure and compliant with modern security standards.
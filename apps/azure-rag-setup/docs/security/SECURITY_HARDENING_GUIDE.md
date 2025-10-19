# Security Hardening Guide for Azure RAG System

## Overview

This guide provides comprehensive security hardening recommendations for the Azure RAG System. The guide covers
system-level security configurations, container security best practices, network segmentation recommendations, and
data encryption enhancements to complement the existing deployment security measures.

## 1. System-Level Security Configurations

### 1.1 SSH Security Hardening

#### Restrict SSH Access

```bash

# Edit SSH configuration

sudo nano /etc/ssh/sshd_config

# Add or modify the following settings

Port 2222  # Change default SSH port
PermitRootLogin no
AllowUsers deploy
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

```

#### Implement SSH Key-Based Authentication

```bash

# Generate SSH key pair on client machine

ssh-keygen -t ed25519 -C "azure-rag-admin"

# Copy public key to server

ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@YOUR_SERVER_IP

# Restart SSH service

sudo systemctl restart sshd

```

#### Configure SSH Firewall Rules

```bash

# Allow SSH only from specific IPs

sudo ufw delete allow 22/tcp
sudo ufw allow from YOUR_ADMIN_IP to any port 2222

```

### 1.2 Fail2Ban Implementation

#### Install and Configure Fail2Ban

```bash

# Install Fail2Ban

sudo apt update
sudo apt install fail2ban

# Create local configuration

sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Edit configuration

sudo nano /etc/fail2ban/jail.local

```

#### Configure SSH Protection

```ini

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

```

#### Start Fail2Ban Service

```bash

# Enable and start Fail2Ban

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status

sudo fail2ban-client status sshd

```

### 1.3 System Updates and Patching

#### Enable Automatic Security Updates

```bash

# Install unattended-upgrades

sudo apt install unattended-upgrades

# Configure automatic updates

sudo dpkg-reconfigure -plow unattended-upgrades

# Edit configuration (2)

sudo nano /etc/apt/apt.conf.d/50unattended-upgrades

```

#### Configure Update Settings

```bash

# In /etc/apt/apt.conf.d/50unattended-upgrades

Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::SyslogEnable "true";

```

#### Schedule Updates

```bash

# Edit auto-update configuration

sudo nano /etc/apt/apt.conf.d/20auto-upgrades

# Add the following

APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";

```

### 1.4 Kernel Security Parameters

#### Configure Sysctl Settings

```bash

# Create sysctl configuration file

sudo nano /etc/sysctl.d/99-azure-rag-security.conf

```

#### Add Security Parameters

```bash

# Network security

net.ipv4.tcp_syncookies = 1
net.ipv4.ip_forward = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# TCP hardening

net.ipv4.tcp_rfc1337 = 1
net.ipv4.tcp_timestamps = 0

# Hide kernel pointers

kernel.kptr_restrict = 2

# Restrict access to dmesg

kernel.dmesg_restrict = 1

# Enable ASLR

kernel.randomize_va_space = 2

```

#### Apply Settings

```bash

# Apply sysctl settings

sudo sysctl -p /etc/sysctl.d/99-azure-rag-security.conf

```

## 2. Container Security Best Practices

### 2.1 Docker Security Configuration

#### Create Docker Daemon Configuration

```bash

# Create daemon configuration file

sudo mkdir -p /etc/docker
sudo nano /etc/docker/daemon.json

```

#### Add Security Settings

```json

{
  "icc": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userland-proxy": false,
  "no-new-privileges": true,
  "live-restore": true,
  "userns-remap": "default"
}

```

#### Restart Docker Service

```bash

# Restart Docker with new configuration

sudo systemctl restart docker

```

### 2.2 Container Runtime Security

#### Implement Docker Bench Security

```bash

# Run Docker Bench Security audit

docker run --rm --net host --pid host --userns host --cap-add audit_control \
    -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
    -v /var/lib:/var/lib \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /usr/lib/systemd:/usr/lib/systemd \
    -v /etc:/etc --label docker_bench_security \
    docker/docker-bench-security

```

#### Add Security Options to Docker Compose

```yaml

# In docker-compose.yml, add security options to each service

services:
  elasticsearch:
    # ... existing configuration ...
    security_opt:

      - no-new-privileges:true

    read_only: true
    tmpfs:

      - /tmp

    cap_drop:

      - ALL

    cap_add:

      - SETGID
      - SETUID
      - DAC_OVERRIDE

```

### 2.3 Container Image Security

#### Implement Image Scanning

```bash

# Install Trivy for vulnerability scanning

sudo apt install trivy

# Scan images regularly

trivy image docker.elastic.co/elasticsearch/elasticsearch:8.11.0
trivy image apache/tika:latest-full

```

#### Create Image Scanning Script

```bash

# Create script for regular scanning

sudo nano /usr/local/bin/scan-container-images.sh

```

```bash

#!/bin/bash

# Container Image Security Scanner

IMAGES=(
  "docker.elastic.co/elasticsearch/elasticsearch:8.11.0"
  "apache/tika:latest-full"
)

for image in "${IMAGES[@]}"; do
  echo "Scanning $image..."
  trivy image --severity HIGH,CRITICAL "$image"
  echo "----------------------------------------"
done

```

```bash

# Make script executable

sudo chmod +x /usr/local/bin/scan-container-images.sh

# Add to crontab for weekly scanning

echo "0 2 * * 0 /usr/local/bin/scan-container-images.sh > /var/log/container-scan.log 2>&1" | sudo crontab -

```

## 3. Network Segmentation Recommendations

### 3.1 Enhanced Firewall Configuration

#### Create Service-Specific Firewall Rules

```bash

# Create custom firewall rules for internal services

sudo nano /etc/ufw/applications.d/azure-rag

```

#### Add Application Profiles

```ini

[Azure-RAG-API]
title=Azure RAG API
description=Azure RAG System API Service
ports=5001/tcp

[Azure-RAG-Elasticsearch]
title=Azure RAG Elasticsearch
description=Azure RAG System Elasticsearch Service
ports=9200/tcp

[Azure-RAG-Tika]
title=Azure RAG Tika
description=Azure RAG System Tika Service
ports=9998/tcp

```

#### Apply Network Segmentation

```bash

# Allow only specific internal connections

sudo ufw allow from 172.28.0.0/16 to any port 9200
sudo ufw allow from 172.28.0.0/16 to any port 9998

```

### 3.2 Network Monitoring

#### Install and Configure Network Monitoring Tools

```bash

# Install network monitoring tools

sudo apt install ntopng

# Configure ntopng

sudo nano /etc/ntopng/ntopng.conf

```

#### Add Network Monitoring to Docker Compose

```yaml

# Add network monitoring service to docker-compose.yml

  ntopng:
    image: ntopng/ntopng:stable
    container_name: ntopng
    privileged: true
    network_mode: host
    volumes:

      - ./data/ntopng:/var/lib/ntopng
      - /etc/localtime:/etc/localtime:ro

    environment:

      - NTOPNG_CMDLINE="-i eth0 -w 3000 -G /var/run/ntopng.pid"

    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

```

## 4. Data Encryption Enhancements

### 4.1 Backup Encryption

#### Implement GPG Backup Encryption

```bash

# Generate GPG key for backup encryption

gpg --gen-key

# Create encrypted backup script

sudo nano /usr/local/bin/encrypted-backup.sh

```

```bash

#!/bin/bash

# Encrypted Backup Script for Azure RAG System

BACKUP_DIR="/backup/azure-rag"
ENCRYPTED_BACKUP_DIR="/backup/azure-rag-encrypted"
DATE=$(date +%Y%m%d_%H%M%S)
GPG_RECIPIENT="backup@azure-rag.local"

# Create backup using existing script

cd /opt/azure-rag-setup
./scripts/backup.sh

# Encrypt backup files

if [ -d "$BACKUP_DIR/$DATE" ]; then
  echo "Encrypting backup: $DATE"

  # Create encrypted backup directory
  mkdir -p "$ENCRYPTED_BACKUP_DIR/$DATE"

  # Encrypt each file
  find "$BACKUP_DIR/$DATE" -type f | while read file; do
    relative_path="${file#$BACKUP_DIR/$DATE/}"
    gpg --encrypt --recipient "$GPG_RECIPIENT" --output "$ENCRYPTED_BACKUP_DIR/$DATE/$relative_path.gpg" "$file"
  done

  echo "Backup encrypted successfully"
else
  echo "Backup directory not found: $BACKUP_DIR/$DATE"
  exit 1
fi

```

```bash

# Make script executable (2)

sudo chmod +x /usr/local/bin/encrypted-backup.sh

# Update cron job to use encrypted backup

# Edit crontab

sudo crontab -e

# Replace backup line with

# 0 2 * * * /usr/local/bin/encrypted-backup.sh >> /var/log/azure-rag-encrypted-backup.log 2>&1

```

### 4.2 Volume Encryption at Rest

#### Implement LUKS Encryption for Docker Volumes

```bash

# Create encrypted volume for sensitive data

sudo dd if=/dev/zero of=/encrypted-data.img bs=1G count=50
sudo cryptsetup luksFormat /encrypted-data.img

# Open encrypted volume

sudo cryptsetup luksOpen /encrypted-data.img encrypted-data

# Create filesystem

sudo mkfs.ext4 /dev/mapper/encrypted-data

# Mount encrypted volume

sudo mkdir -p /encrypted-data
sudo mount /dev/mapper/encrypted-data /encrypted-data

# Update Docker Compose to use encrypted volumes

# In docker-compose.yml

# volumes

#   elastic_data

#     driver: local

#     driver_opts

#       type: none

#       o: bind

#       device: /encrypted-data/elasticsearch

```

### 4.3 Key Management

#### Implement Key Management System

```bash

# Install HashiCorp Vault for key management

docker run -d --name vault \
  --cap-add=IPC_LOCK \
  -p 8200:8200 \
  -v /data/vault/config:/vault/config \
  -v /data/vault/data:/vault/data \
  -v /data/vault/logs:/vault/logs \
  vault:latest

# Configure Vault

docker exec -it vault sh
vault operator init
vault operator unseal  # Run 3 times with different unseal keys

```

## 5. Implementation Checklist

### 5.1 System-Level Security

- [ ] SSH port changed from 22 to custom port
- [ ] SSH key-based authentication enabled
- [ ] SSH password authentication disabled
- [ ] Fail2Ban installed and configured
- [ ] Automatic security updates enabled
- [ ] Kernel security parameters configured
- [ ] System rebooted to apply all changes

### 5.2 Container Security

- [ ] Docker daemon security options configured
- [ ] Container security options added to docker-compose.yml
- [ ] Container image scanning implemented
- [ ] Regular vulnerability scanning scheduled
- [ ] Docker Bench Security audit performed

### 5.3 Network Security

- [ ] Service-specific firewall rules implemented
- [ ] Internal network segmentation configured
- [ ] Network monitoring tools installed
- [ ] Network traffic analysis baseline established

### 5.4 Data Encryption

- [ ] Backup encryption implemented
- [ ] GPG keys generated and secured
- [ ] Volume encryption at rest configured
- [ ] Key management system deployed
- [ ] Encryption keys properly backed up

## 6. Security Testing and Validation

### 6.1 Security Audit Script

```bash

# Create security audit script

sudo nano /usr/local/bin/security-audit.sh

```

```bash

#!/bin/bash

# Azure RAG System Security Audit

echo "=== Azure RAG System Security Audit ==="
echo "Date: $(date)"
echo ""

echo "1. SSH Configuration:"
sudo sshd -T | grep -E "(port|permitrootlogin|passwordauthentication|maxauthtries)"

echo ""
echo "2. Firewall Status:"
sudo ufw status

echo ""
echo "3. Fail2Ban Status:"
sudo fail2ban-client status

echo ""
echo "4. Docker Security Options:"
docker info --format "Security Options: {{.SecurityOptions}}"

echo ""
echo "5. Container Vulnerabilities:"
echo "Run: trivy image [image-name] for each container image"

echo ""
echo "6. System Updates:"
apt list --upgradable 2>/dev/null | grep -v "Listing..."

echo ""
echo "7. Encryption Status:"
lsblk | grep crypt

echo ""
echo "Security audit completed."

```

```bash

# Make script executable (3)

sudo chmod +x /usr/local/bin/security-audit.sh

# Run audit

sudo /usr/local/bin/security-audit.sh

```

## 7. Ongoing Security Maintenance

### 7.1 Regular Security Tasks

1. **Weekly**: Run container image vulnerability scans
2. **Monthly**: Perform security audit using audit script
3. **Quarterly**: Review and update firewall rules
4. **Annually**: Rotate encryption keys and SSH keys

### 7.2 Monitoring and Alerting

1. Set up alerts for failed login attempts
2. Monitor for unauthorized network connections
3. Track container security vulnerabilities
4. Monitor backup encryption status

This security hardening guide provides a comprehensive approach to enhancing the security posture of the Azure RAG
System beyond the existing deployment security measures. Implementation should be done systematically
  , testing each component before moving to the next.

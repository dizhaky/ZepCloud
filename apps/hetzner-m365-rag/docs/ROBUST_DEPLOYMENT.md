# Robust Deployment for M365 RAG System

## Overview

This document describes how to use the robust deployment and verification scripts for the M365 RAG System. These scripts
  provide enhanced error handling, validation, and status reporting compared to the basic deployment scripts.

## Deployment Script (`robust-deploy.sh`)

The robust deployment script performs the following functions:

1. **Dependency Checking**: Verifies that all required system dependencies are installed
2. **Environment Validation**: Ensures environment configuration is properly set up
3. **SSL Certificate Setup**: Generates SSL certificates if needed
4. **Firewall Configuration**: Sets up UFW firewall rules
5. **Service Deployment**: Starts all services using Docker Compose
6. **Service Verification**: Checks that all services are running correctly

### Prerequisites

Before running the deployment script, ensure you have:

1. A Unix-like environment (Linux, macOS, WSL)
2. Bash shell
3. Root or sudo access
4. All required dependencies installed (Docker, Docker Compose, Git, etc.)

### Running the Deployment Script

```bash

# Navigate to the scripts directory

cd /path/to/m365-rag-system/scripts

# Make the script executable

chmod +x robust-deploy.sh

# Run the script as root or with sudo

sudo ./robust-deploy.sh

```

### Script Phases

The deployment script runs through several phases:

1. **Dependency Check**: Verifies all required system dependencies
2. **Environment Validation**: Checks environment configuration and required variables
3. **SSL Setup**: Generates SSL certificates if needed
4. **Firewall Configuration**: Sets up UFW firewall rules
5. **Service Startup**: Starts all services using Docker Compose
6. **Service Verification**: Checks that all services are running correctly

### Error Handling

The script includes comprehensive error handling:

- Checks for missing dependencies and provides installation guidance
- Validates environment variables and provides clear error messages
- Handles service startup failures gracefully
- Provides detailed logging to `/var/log/m365-rag-deploy.log`

## Verification Script (`verify-deployment.sh`)

The verification script checks if all services are running correctly and provides a comprehensive status report.

### Running the Verification Script

```bash

# Navigate to the scripts directory (2)

cd /path/to/m365-rag-system/scripts

# Make the script executable (2)

chmod +x verify-deployment.sh

# Run the script as root or with sudo (2)

sudo ./verify-deployment.sh

```

### Verification Checks

The verification script performs the following checks:

1. **Docker Services**: Checks that Docker services are running and healthy
2. **Service Endpoints**: Verifies that all service endpoints are accessible
3. **System Resources**: Checks disk space, memory usage, and CPU load
4. **Security Configuration**: Verifies firewall status and environment file permissions
5. **Backup Configuration**: Checks backup script, directory, and cron job status
6. **Status Report**: Generates a comprehensive status report

### Status Report

The verification script generates a detailed status report in `/tmp/` with the following information:

- System information
- Docker version and status
- Disk usage
- Memory usage
- CPU load
- Network connections
- Firewall status

## Best Practices

### Before Deployment

1. **Review Environment Configuration**: Ensure all required environment variables are set in `.env`
2. **Check System Resources**: Verify sufficient disk space, memory, and CPU for the deployment
3. **Review Security Settings**: Ensure firewall rules and security settings meet your requirements

### During Deployment

1. **Monitor Progress**: Watch the console output for status updates and potential issues
2. **Check Logs**: Review `/var/log/m365-rag-deploy.log` for detailed information
3. **Handle Warnings**: Address any warnings that may affect system performance or security

### After Deployment

1. **Run Verification**: Use the verification script to confirm all services are running correctly
2. **Test Functionality**: Verify that all system components are working as expected
3. **Monitor Logs**: Check service logs for any errors or warnings
4. **Review Status Report**: Examine the generated status report for system health information

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:

   ```bash
   # Install Docker
   sudo apt install docker.io docker-compose

   # Install other dependencies
   sudo apt install git curl openssl ufw jq
   ```

2. **Environment File Issues**:

   ```bash
   # Check environment file
   cat /data/m365-rag/.env

   # Ensure proper permissions
   chmod 600 /data/m365-rag/.env
   ```

3. **Service Startup Failures**:

   ```bash
   # Check service status
   cd /data/m365-rag && docker compose ps

   # Check service logs
   cd /data/m365-rag && docker compose logs --tail=100
   ```

4. **Firewall Issues**:

   ```bash
   # Check firewall status
   sudo ufw status

   # Allow required ports
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

### Diagnostic Commands

```bash

# Check Docker status

systemctl status docker

# Check environment variables

cat /data/m365-rag/.env

# Check service status

cd /data/m365-rag && docker compose ps

# Check service logs

cd /data/m365-rag && docker compose logs --tail=50

# Check system resources

df -h
free -h
uptime

# Check firewall status

sudo ufw status

```

## Security Considerations

### Environment File Security

Ensure your `.env` file is properly secured:

```bash

# Set proper permissions

chmod 600 /data/m365-rag/.env

# Never commit to version control

echo ".env" >> .gitignore

```

### Firewall Configuration

The deployment script configures the firewall with the following rules:

- SSH (22/tcp): Allowed (consider restricting to specific IPs)
- HTTP (80/tcp): Allowed
- HTTPS (443/tcp): Allowed

For production environments, consider:

1. Restricting SSH access to specific IP addresses
2. Implementing fail2ban for brute force protection
3. Regularly reviewing firewall rules

## Logging

Both scripts generate detailed logs:

- Deployment log: `/var/log/m365-rag-deploy.log`
- Verification log: `/var/log/m365-rag-verify.log`

These logs contain timestamped entries for all actions performed by the scripts and can be used for troubleshooting and
  auditing purposes.

## Automation

You can automate deployment verification in your monitoring system:

```bash

# Run verification check and exit on failure

./verify-deployment.sh && echo "Verification successful" || echo "Verification failed"

```

## Conclusion

The robust deployment and verification scripts provide a comprehensive solution for deploying and monitoring the M365
RAG System. They include extensive error handling, validation, and reporting features to ensure a successful
  deployment and ongoing system health monitoring.

# Deployment Preparation for M365 RAG System

## Overview

This document explains how to use the deployment preparation script (`deployment-prep.sh`) to check system dependencies, validate environment configuration, and prepare for deploying the M365 RAG System in a production environment.

## Purpose

The deployment preparation script performs several important functions:

1. **Dependency Checking**: Verifies that all required system dependencies are installed
2. **Configuration Validation**: Ensures environment configuration is properly set up
3. **Security Assessment**: Checks password strength and security settings
4. **Setup Guidance**: Provides instructions for Azure AD application configuration
5. **Next Steps**: Outlines the deployment process

## Running the Script

### Prerequisites

Before running the deployment preparation script, ensure you have:

1. A Unix-like environment (Linux, macOS, WSL)
2. Bash shell
3. Root or sudo access (recommended for full functionality)

### Execution

To run the deployment preparation script:

```bash
# Navigate to the scripts directory
cd /path/to/m365-rag-system/scripts

# Make the script executable
chmod +x deployment-prep.sh

# Run the script (as root or with sudo for full functionality)
sudo ./deployment-prep.sh
```

## Script Phases

The deployment preparation script runs through several phases to validate your environment:

### Phase 1: System Dependencies

This phase checks for essential system commands and services:

- **Docker**: Container runtime platform
- **Docker Compose**: Multi-container Docker applications
- **Git**: Version control system
- **Curl**: Command-line tool for transferring data
- **OpenSSL**: Cryptography toolkit
- **UFW**: Uncomplicated Firewall

### Phase 2: Environment Configuration

This phase validates your environment configuration:

- **Environment File**: Checks for `.env` file existence
- **Docker Compose Configuration**: Verifies `docker-compose.yml`
- **Deployment Script**: Ensures `deploy.sh` exists
- **Required Variables**: Validates essential environment variables are set
- **Password Strength**: Checks that passwords meet security requirements

### Phase 3: SSL Configuration

This phase checks SSL certificate configuration:

- **Elasticsearch Certificates**: Verifies SSL certificates for Elasticsearch
- **Certificate Authority**: Checks for CA certificate
- **Private Keys**: Ensures private keys are properly configured

### Phase 4: Firewall Configuration

This phase validates firewall settings:

- **UFW Status**: Checks if firewall is active
- **Required Ports**: Verifies ports 22, 80, and 443 are allowed

### Phase 5: Azure AD Application Setup

This phase provides instructions for setting up Azure AD application registration for M365 integration.

### Phase 6: Next Steps

This phase provides guidance on completing the deployment process.

## Interpreting Results

### Success Indicators

- ✅ Green checkmarks indicate successful checks
- Configuration files found
- Required services running
- Strong passwords configured

### Warning Indicators

- ⚠️ Yellow warnings indicate potential issues that should be addressed
- Missing optional components
- Weak password recommendations
- Non-critical configuration issues

### Error Indicators

- ❌ Red X marks indicate critical issues that must be resolved
- Missing required dependencies
- Critical configuration errors
- Security vulnerabilities

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```bash
   # Install Docker
   sudo apt install docker.io docker-compose
   
   # Install other dependencies
   sudo apt install git curl openssl ufw
   ```

2. **Environment File Not Found**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit with your values
   nano .env
   ```

3. **Weak Passwords**:
   ```bash
   # Generate strong passwords
   openssl rand -base64 32
   ```

4. **Firewall Not Configured**:
   ```bash
   # Run firewall setup script
   sudo ./setup-firewall.sh
   ```

### Diagnostic Commands

```bash
# Check Docker status
systemctl status docker

# Check environment variables
cat .env

# Check firewall status
sudo ufw status

# Check SSL certificates
ls -la config/elasticsearch/certs/
```

## Azure AD Application Setup

The script provides detailed instructions for setting up Azure AD application registration:

1. **Register Application**:
   - Go to Azure Portal
   - Navigate to App registrations
   - Create new registration

2. **Configure API Permissions**:
   - Add Microsoft Graph permissions
   - Grant admin consent

3. **Create Client Secret**:
   - Generate client secret
   - Note the secret value

4. **Update Environment File**:
   - Add M365_CLIENT_ID
   - Add M365_CLIENT_SECRET
   - Add M365_TENANT_ID

## Security Considerations

### Password Requirements

The script validates that passwords meet security requirements:

- **Minimum Length**: 12 characters recommended
- **Complexity**: Mix of letters, numbers, and special characters
- **Uniqueness**: Unique passwords for each service

### Environment File Security

Ensure your `.env` file is properly secured:

```bash
# Set proper permissions
chmod 600 .env

# Never commit to version control
echo ".env" >> .gitignore
```

## Next Steps After Preparation

After running the deployment preparation script:

1. **Configure Azure AD Application** (if not already done)
2. **Update Environment File** with your credentials
3. **Generate SSL Certificates** if needed
4. **Run Deployment Script**:
   ```bash
   ./deploy.sh
   ```

## Automation

You can automate the preparation check in your deployment pipeline:

```bash
# Run preparation check and exit on failure
./deployment-prep.sh && echo "Preparation successful" || echo "Preparation failed"
```

## Best Practices

1. **Regular Validation**: Run the preparation script regularly to ensure configuration remains valid
2. **Documentation**: Keep documentation of your environment configuration
3. **Security Reviews**: Regularly review password strength and security settings
4. **Dependency Updates**: Keep system dependencies updated
5. **Backup Configuration**: Ensure backup configuration is properly set up

This deployment preparation process ensures your M365 RAG System is properly configured and ready for production deployment.
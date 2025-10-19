# Firewall Configuration for M365 RAG System

## Overview

This document describes the firewall configuration for the M365 RAG System in a production environment. The firewall is
  a critical security component that controls network access to and from the system.

## Firewall Technology

The M365 RAG System uses **UFW (Uncomplicated Firewall)** as the firewall management tool. UFW provides a simplified
  interface for managing iptables firewall rules.

## Default Policies

The firewall is configured with the following default policies:

- **Incoming connections**: DENY (default deny policy)
- **Outgoing connections**: ALLOW (default allow policy)

This configuration follows security best practices by explicitly allowing only necessary incoming connections while
  permitting all outgoing traffic.

## Allowed Incoming Connections

The following ports are open for incoming connections:

| Port | Protocol | Service | Purpose |
|------|----------|---------|---------|
| 22 | TCP | SSH | Secure remote administration |
| 80 | TCP | HTTP | Web interface access |
| 443 | TCP | HTTPS | Secure web interface access |

## Security Considerations

### SSH Security

While SSH access is allowed on port 22, it is highly recommended to:

1. **Restrict SSH access to specific IP addresses**:

   ```bash
   # Remove open SSH rule
   sudo ufw delete allow 22/tcp

   # Allow SSH only from specific IP
   sudo ufw allow from YOUR_IP_ADDRESS to any port 22
   ```

2. **Use key-based authentication** instead of passwords
3. **Change the default SSH port** if possible
4. **Implement fail2ban** to prevent brute force attacks

### HTTP/HTTPS Access

HTTP (port 80) and HTTPS (port 443) are open to allow web interface access. In a production environment:

1. **Ensure HTTPS is enforced** with proper SSL certificates
2. **Redirect all HTTP traffic to HTTPS**
3. **Implement proper access controls** at the application level

## Advanced Configuration

### Rate Limiting

To prevent brute force attacks, you can implement rate limiting:

```bash

# Rate limit SSH connections (6 connections per 30 seconds)

sudo ufw limit ssh

```

### Logging

Enable logging for security monitoring:

```bash

# Enable logging

sudo ufw logging on

# Set log level (low, medium, high, full)

sudo ufw logging medium

```

## Management Commands

### Viewing Rules

```bash

# View all rules with numbers

sudo ufw status numbered

# View verbose status

sudo ufw status verbose

```

### Adding Rules

```bash

# Allow a specific port

sudo ufw allow PORT_NUMBER

# Allow a specific port with comment

sudo ufw allow PORT_NUMBER comment 'DESCRIPTION'

# Allow a specific IP

sudo ufw allow from IP_ADDRESS

# Allow a specific IP to a specific port

sudo ufw allow from IP_ADDRESS to any port PORT_NUMBER

```

### Deleting Rules

```bash

# Delete by rule

sudo ufw delete allow PORT_NUMBER

# Delete by number (use 'ufw status numbered' to see numbers)

sudo ufw delete RULE_NUMBER

```

### Disabling/Enabling

```bash

# Disable firewall

sudo ufw disable

# Enable firewall

sudo ufw enable

# Reset all rules

sudo ufw reset

```

## Monitoring

Regular monitoring of the firewall is essential for security:

```bash

# View firewall logs

sudo tail -f /var/log/ufw.log

# View recent firewall activity

sudo grep UFW /var/log/syslog

```

## Backup and Restore

### Backup Rules

```bash

# Export current rules

sudo ufw status numbered > firewall-rules-backup.txt

```

### Restore Rules

```bash

# Manually reapply rules from backup

# Or use the setup-firewall.sh script

```

## Troubleshooting

### Common Issues

1. **Can't connect to services**: Check if the required ports are allowed
2. **SSH connection refused**: Verify SSH port is allowed and SSH service is running
3. **Web interface not accessible**: Ensure ports 80 and 443 are allowed

### Diagnostic Commands

```bash

# Check if firewall is active

sudo ufw status

# Test port connectivity

nc -zv HOSTNAME PORT

# View network connections

sudo netstat -tulpn

```

## Best Practices

1. **Regular review**: Periodically review firewall rules
2. **Principle of least privilege**: Only allow necessary connections
3. **Documentation**: Keep documentation of all firewall rules
4. **Testing**: Test firewall configuration after changes
5. **Monitoring**: Monitor firewall logs for suspicious activity
6. **Updates**: Keep the system and firewall software updated

This firewall configuration provides a solid security foundation for the M365 RAG System while allowing necessary access
  for administration and user services.

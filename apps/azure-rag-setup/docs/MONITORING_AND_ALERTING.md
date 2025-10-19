# Monitoring and Alerting Configuration for Azure RAG System

## Overview

This document provides a comprehensive monitoring and alerting configuration for the Azure RAG System that enhances the existing error monitoring capabilities. The configuration includes log aggregation setup, intrusion detection system recommendations, security event monitoring, and automated security scanning.

## 1. Log Aggregation Setup

### 1.1 Centralized Logging Architecture

The Azure RAG System implements a centralized logging architecture using the ELK stack (Elasticsearch, Logstash, Kibana) that's already partially in place with Elasticsearch.

#### Current Logging Components:
- Elasticsearch for log storage and indexing
- Docker container logs
- Application logs from M365 indexing processes
- System logs

#### Enhanced Log Aggregation Setup:

```bash
# Create a dedicated log directory
sudo mkdir -p /var/log/azure-rag-system
sudo chown -R deploy:deploy /var/log/azure-rag-system
sudo chmod 755 /var/log/azure-rag-system
```

#### Configure Docker Log Rotation:
```bash
# Update docker-compose.yml with log rotation settings
# Add to each service in docker-compose.yml:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

#### Set up Logstash for Log Processing:
```bash
# Create Logstash configuration directory
sudo mkdir -p /etc/logstash/conf.d

# Create Logstash configuration file
sudo nano /etc/logstash/conf.d/azure-rag.conf
```

```ruby
input {
  file {
    path => "/var/log/azure-rag-system/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
    }
  }
  
  file {
    path => "/opt/azure-rag-setup/m365_final_sync_*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
  
  docker {
    host => "unix:///var/run/docker.sock"
  }
}

filter {
  # Parse application logs
  if [message] =~ /\[.*\]/ {
    grok {
      match => { "message" => "\[%{TIMESTAMP_ISO8601:timestamp}\] %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
  
  # Parse error patterns
  if [message] =~ /(?i)(error|exception|fail)/ {
    mutate {
      add_tag => [ "error" ]
    }
  }
  
  # Parse security-related logs
  if [message] =~ /(?i)(authentication|authorization|access denied|unauthorized)/ {
    mutate {
      add_tag => [ "security" ]
    }
  }
  
  # Parse rate limiting events
  if [message] =~ /(?i)(rate limit|429)/ {
    mutate {
      add_tag => [ "rate_limit" ]
    }
  }
  
  # Add geoip for network-related logs (if applicable)
  if [clientip] {
    geoip {
      source => "clientip"
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "azure-rag-logs-%{+YYYY.MM.dd}"
    user => "elastic"
    password => "${ELASTIC_PASSWORD}"
  }
  
  # Send critical alerts to a separate index
  if "error" in [tags] or "security" in [tags] {
    elasticsearch {
      hosts => ["localhost:9200"]
      index => "azure-rag-alerts-%{+YYYY.MM.dd}"
      user => "elastic"
      password => "${ELASTIC_PASSWORD}"
    }
  }
}
```

### 1.2 Log File Structure

#### Application Logs:
- `/var/log/azure-rag-system/application.log` - Main application logs
- `/var/log/azure-rag-system/security.log` - Security-related events
- `/var/log/azure-rag-system/access.log` - Access logs
- `/var/log/azure-rag-system/error.log` - Error logs

#### System Logs:
- `/var/log/azure-rag-system/system.log` - System-level events
- `/var/log/azure-rag-system/audit.log` - Audit trail
- `/var/log/azure-rag-system/docker.log` - Docker container logs

#### M365 Integration Logs:
- `/var/log/azure-rag-system/m365-sync.log` - M365 synchronization logs
- `/var/log/azure-rag-system/m365-auth.log` - Authentication logs

### 1.3 Log Rotation Configuration

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/azure-rag-system
```

```
/var/log/azure-rag-system/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 deploy deploy
    postrotate
        systemctl reload azure-rag-system > /dev/null 2>&1 || true
    endscript
}
```

## 2. Intrusion Detection System Recommendations

### 2.1 Host-Based Intrusion Detection System (HIDS)

#### Install and Configure OSSEC:
```bash
# Install OSSEC HIDS
sudo apt update
sudo apt install ossec-hids

# Configure OSSEC
sudo nano /var/ossec/etc/ossec.conf
```

```xml
<ossec_config>
  <global>
    <email_notification>no</email_notification>
    <jsonout_output>yes</jsonout_output>
    <alerts_log>yes</alerts_log>
    <logall>no</logall>
    <logall_json>no</logall_json>
  </global>

  <alerts>
    <log_alert_level>3</log_alert_level>
    <email_alert_level>12</email_alert_level>
  </alerts>

  <!-- Configure syscheck for file integrity monitoring -->
  <syscheck>
    <frequency>7200</frequency>
    <directories check_all="yes">/opt/azure-rag-setup</directories>
    <directories check_all="yes">/etc/ssl</directories>
    <ignore>/opt/azure-rag-setup/m365_final_sync_*.log</ignore>
  </syscheck>

  <!-- Configure rootcheck for rootkit detection -->
  <rootcheck>
    <rootkit_files>/var/ossec/etc/shared/rootkit_files.txt</rootkit_files>
    <rootkit_trojans>/var/ossec/etc/shared/rootkit_trojans.txt</rootkit_trojans>
    <system_audit>/var/ossec/etc/shared/system_audit_rcl.txt</system_audit>
  </rootcheck>

  <!-- Configure active response -->
  <active-response>
    <disabled>no</disabled>
  </active-response>

  <!-- Configure localfile for log monitoring -->
  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/auth.log</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/syslog</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/azure-rag-system/*.log</location>
  </localfile>
</ossec_config>
```

#### Start OSSEC Service:
```bash
# Enable and start OSSEC
sudo systemctl enable ossec
sudo systemctl start ossec

# Check status
sudo systemctl status ossec
```

### 2.2 Network-Based Intrusion Detection System (NIDS)

#### Install and Configure Suricata:
```bash
# Install Suricata
sudo apt update
sudo apt install suricata

# Configure Suricata
sudo nano /etc/suricata/suricata.yaml
```

```yaml
# Suricata configuration for Azure RAG System
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "$HOME_NET"
    SMTP_SERVERS: "$HOME_NET"
    SQL_SERVERS: "$HOME_NET"
    DNS_SERVERS: "$HOME_NET"
    TELNET_SERVERS: "$HOME_NET"
    AIM_SERVERS: "$EXTERNAL_NET"
    DC_SERVERS: "$HOME_NET"
    DNP3_SERVER: "$HOME_NET"
    DNP3_CLIENT: "$HOME_NET"
    MODBUS_CLIENT: "$HOME_NET"
    MODBUS_SERVER: "$HOME_NET"
    ENIP_CLIENT: "$HOME_NET"
    ENIP_SERVER: "$HOME_NET"

default-rule-path: /etc/suricata/rules
rule-files:
 - suricata.rules

# Configure network interfaces
af-packet:
  - interface: eth0
    threads: 2
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

# Configure logging
outputs:
  - fast:
      enabled: yes
      filename: /var/log/suricata/fast.log

  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      pcap-file: false
      community-id: false
      community-id-seed: 0
      xff:
        enabled: no
      types:
        - alert:
            tagged-packets: yes
        - anomaly:
            enabled: yes
            types:
              decode: yes
              stream: yes
              applayer: yes
          packethdr: no
        - http:
            extended: yes
        - dns:
            query: yes
            answer: yes
        - tls:
            extended: yes
        - files:
            force-magic: no
        - smtp:
            extended: yes
        - ssh
        - stats:
            totals: yes
            threads: no
        - flow
        - netflow
```

#### Update Suricata Rules:
```bash
# Update rules
sudo suricata-update

# Enable and start Suricata
sudo systemctl enable suricata
sudo systemctl start suricata
```

## 3. Security Event Monitoring

### 3.1 Security Information and Event Management (SIEM)

#### Configure Elasticsearch for Security Monitoring:
```bash
# Create security monitoring index template
curl -X PUT "localhost:9200/_template/security-monitoring" \
  -H 'Content-Type: application/json' \
  -u "elastic:$ELASTIC_PASSWORD" \
  -d '{
    "index_patterns": ["security-*"],
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 1
    },
    "mappings": {
      "properties": {
        "timestamp": { "type": "date" },
        "event_type": { "type": "keyword" },
        "severity": { "type": "keyword" },
        "source_ip": { "type": "ip" },
        "destination_ip": { "type": "ip" },
        "user": { "type": "keyword" },
        "action": { "type": "keyword" },
        "resource": { "type": "keyword" },
        "message": { "type": "text" }
      }
    }
  }'
```

#### Create Security Monitoring Dashboard:
```bash
# Create Kibana dashboard configuration
# This would typically be done through the Kibana UI or API
# Below is a sample configuration for reference
```

### 3.2 Security Event Types to Monitor

#### Authentication Events:
- Failed login attempts
- Successful logins
- Account lockouts
- Password changes

#### Authorization Events:
- Access denied events
- Privilege escalation attempts
- Resource access patterns

#### System Events:
- Process execution
- File system changes
- Network connections
- System configuration changes

#### Application Events:
- API access patterns
- Data access requests
- Error conditions
- Rate limiting events

### 3.3 Security Event Correlation

#### Create Security Event Correlation Rules:
```bash
# Create correlation script
sudo nano /usr/local/bin/security-event-correlation.sh
```

```bash
#!/bin/bash
# Security Event Correlation Script for Azure RAG System

# Configuration
ELASTIC_HOST="localhost:9200"
ELASTIC_USER="elastic"
ELASTIC_PASSWORD="${ELASTIC_PASSWORD:-YourStrongPassword123!}"
ALERT_EMAIL="admin@yourdomain.com"

# Function to send alerts
send_alert() {
    local subject="$1"
    local message="$2"
    
    # Log alert
    echo "$(date): ALERT - $subject" >> /var/log/azure-rag-system/security-alerts.log
    
    # Send email alert (if mail is configured)
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
    fi
    
    # Send to syslog
    logger -t "AZURE-RAG-SECURITY" "ALERT: $subject"
}

# Check for multiple failed login attempts
failed_logins=$(curl -s -u "$ELASTIC_USER:$ELASTIC_PASSWORD" \
    "http://$ELASTIC_HOST/security-*/_search" \
    -H 'Content-Type: application/json' \
    -d '{
        "query": {
            "bool": {
                "must": [
                    {"term": {"event_type": "authentication"}},
                    {"term": {"action": "failed_login"}},
                    {"range": {"timestamp": {"gte": "now-5m"}}}
                ]
            }
        },
        "aggs": {
            "by_user": {
                "terms": {"field": "user.keyword"},
                "aggs": {
                    "failed_count": {
                        "value_count": {"field": "_id"}
                    }
                }
            }
        }
    }' | jq -r '.aggregations.by_user.buckets[] | select(.failed_count.value > 5) | "User: \(.key), Failed attempts: \(.failed_count.value)"')

if [ -n "$failed_logins" ]; then
    send_alert "Multiple Failed Login Attempts Detected" "Potential brute force attack detected:
$failed_logins"
fi

# Check for suspicious file access patterns
suspicious_access=$(curl -s -u "$ELASTIC_USER:$ELASTIC_PASSWORD" \
    "http://$ELASTIC_HOST/security-*/_search" \
    -H 'Content-Type: application/json' \
    -d '{
        "query": {
            "bool": {
                "must": [
                    {"term": {"event_type": "file_access"}},
                    {"range": {"timestamp": {"gte": "now-10m"}}}
                ]
            }
        },
        "aggs": {
            "by_user": {
                "terms": {"field": "user.keyword"},
                "aggs": {
                    "access_count": {
                        "value_count": {"field": "_id"}
                    }
                }
            }
        }
    }' | jq -r '.aggregations.by_user.buckets[] | select(.access_count.value > 100) | "User: \(.key), File accesses: \(.access_count.value)"')

if [ -n "$suspicious_access" ]; then
    send_alert "Suspicious File Access Pattern Detected" "High volume file access detected:
$suspicious_access"
fi

# Check for unauthorized network connections
unauthorized_connections=$(curl -s -u "$ELASTIC_USER:$ELASTIC_PASSWORD" \
    "http://$ELASTIC_HOST/security-*/_search" \
    -H 'Content-Type: application/json' \
    -d '{
        "query": {
            "bool": {
                "must": [
                    {"term": {"event_type": "network_connection"}},
                    {"term": {"action": "blocked"}},
                    {"range": {"timestamp": {"gte": "now-1h"}}}
                ]
            }
        }
    }' | jq -r '.hits.total.value')

if [ "$unauthorized_connections" -gt 10 ]; then
    send_alert "Multiple Unauthorized Network Connections Blocked" "Blocked $unauthorized_connections unauthorized network connections in the last hour"
fi
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/security-event-correlation.sh

# Add to crontab for regular execution
echo "*/5 * * * * /usr/local/bin/security-event-correlation.sh" | sudo crontab -
```

## 4. Automated Security Scanning

### 4.1 Vulnerability Scanning

#### Install and Configure Clair for Container Scanning:
```bash
# Install Clair scanner
sudo apt install clair

# Configure Clair
sudo nano /etc/clair/config.yaml
```

```yaml
# Clair configuration
clair:
  database:
    type: pgsql
    options:
      source: host=localhost port=5432 user=clair dbname=clair sslmode=disable
      cachesize: 16384

  api:
    port: 6060
    healthport: 6061
    timeout: 900s

  updater:
    interval: 2h
    enabledupdaters:
      - debian
      - ubuntu
      - rhel
      - oracle
      - alpine
      - suse

  notifier:
    attempts: 3
    renotifyinterval: 2h
    http:
      endpoint: http://localhost:6080/notify
```

#### Create Container Scanning Script:
```bash
# Create container scanning script
sudo nano /usr/local/bin/container-security-scan.sh
```

```bash
#!/bin/bash
# Container Security Scanning Script

# Configuration
REPORT_DIR="/var/log/azure-rag-system/security-scans"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$REPORT_DIR"

# Scan Docker images
IMAGES=(
  "docker.elastic.co/elasticsearch/elasticsearch:8.11.0"
  "apache/tika:latest-full"
)

echo "Starting container security scan at $(date)" > "$REPORT_DIR/scan_$DATE.log"

for image in "${IMAGES[@]}"; do
    echo "Scanning image: $image" >> "$REPORT_DIR/scan_$DATE.log"
    
    # Use Trivy for scanning (if installed)
    if command -v trivy &> /dev/null; then
        trivy image --severity HIGH,CRITICAL "$image" >> "$REPORT_DIR/scan_$DATE.log"
    else
        echo "Trivy not installed, skipping scan for $image" >> "$REPORT_DIR/scan_$DATE.log"
    fi
    
    echo "----------------------------------------" >> "$REPORT_DIR/scan_$DATE.log"
done

# Check for critical vulnerabilities
CRITICAL_VULNS=$(grep -c "CRITICAL:" "$REPORT_DIR/scan_$DATE.log" 2>/dev/null || echo 0)
HIGH_VULNS=$(grep -c "HIGH:" "$REPORT_DIR/scan_$DATE.log" 2>/dev/null || echo 0)

if [ "$CRITICAL_VULNS" -gt 0 ] || [ "$HIGH_VULNS" -gt 5 ]; then
    echo "ALERT: Critical or high vulnerabilities detected in container images" | tee -a "$REPORT_DIR/scan_$DATE.log"
    # Send alert (implementation depends on your alerting system)
    logger -t "AZURE-RAG-SECURITY" "CRITICAL: Container vulnerabilities detected"
fi

echo "Container security scan completed at $(date)" >> "$REPORT_DIR/scan_$DATE.log"
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/container-security-scan.sh

# Add to crontab for weekly scanning
echo "0 2 * * 0 /usr/local/bin/container-security-scan.sh" | sudo crontab -
```

### 4.2 File Integrity Monitoring

#### Configure AIDE (Advanced Intrusion Detection Environment):
```bash
# Install AIDE
sudo apt install aide

# Initialize AIDE database
sudo aideinit

# Configure AIDE
sudo nano /etc/aide/aide.conf
```

```
# AIDE configuration for Azure RAG System

# Define rules
AllRules = p+i+n+u+g+s+m+c+acl+selinux+xattrs+sha512

# Monitor critical directories
/opt/azure-rag-setup/ AllRules
/etc/ssl/ AllRules
/etc/docker/ AllRules
/var/log/azure-rag-system/ AllRules

# Exclude log files from monitoring
!/opt/azure-rag-setup/m365_final_sync_*.log
!/var/log/azure-rag-system/*.log

# Database location
database=file:/var/lib/aide/aide.db
database_out=file:/var/lib/aide/aide.db.new
```

#### Create File Integrity Check Script:
```bash
# Create file integrity check script
sudo nano /usr/local/bin/file-integrity-check.sh
```

```bash
#!/bin/bash
# File Integrity Check Script

# Run AIDE check
sudo aide --check > /var/log/azure-rag-system/aide-check-$(date +%Y%m%d_%H%M%S).log 2>&1

# Check for changes
if grep -q "Changed:" /var/log/azure-rag-system/aide-check-$(date +%Y%m%d_%H%M%S).log; then
    echo "ALERT: File integrity changes detected" | logger -t "AZURE-RAG-SECURITY"
    # Send alert
    echo "File integrity changes detected. Check /var/log/azure-rag-system/aide-check-$(date +%Y%m%d_%H%M%S).log for details." | mail -s "File Integrity Alert" admin@yourdomain.com
fi
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/file-integrity-check.sh

# Add to crontab for daily checks
echo "0 3 * * * /usr/local/bin/file-integrity-check.sh" | sudo crontab -
```

### 4.3 Configuration Auditing

#### Create Security Configuration Audit Script:
```bash
# Create security configuration audit script
sudo nano /usr/local/bin/security-config-audit.sh
```

```bash
#!/bin/bash
# Security Configuration Audit Script

REPORT_FILE="/var/log/azure-rag-system/security-audit-$(date +%Y%m%d_%H%M%S).log"

echo "=== Azure RAG System Security Configuration Audit ===" > "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check SSH configuration
echo "1. SSH Configuration:" >> "$REPORT_FILE"
sudo sshd -T | grep -E "(port|permitrootlogin|passwordauthentication|maxauthtries)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check firewall status
echo "2. Firewall Status:" >> "$REPORT_FILE"
sudo ufw status >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check Docker security options
echo "3. Docker Security Options:" >> "$REPORT_FILE"
docker info --format "Security Options: {{.SecurityOptions}}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check system updates
echo "4. System Updates:" >> "$REPORT_FILE"
apt list --upgradable 2>/dev/null | grep -v "Listing..." >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check encryption status
echo "5. Encryption Status:" >> "$REPORT_FILE"
lsblk | grep crypt >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Check for security tools
echo "6. Security Tools:" >> "$REPORT_FILE"
echo "OSSEC: $(systemctl is-active ossec 2>/dev/null || echo 'Not installed/running')" >> "$REPORT_FILE"
echo "Fail2Ban: $(systemctl is-active fail2ban 2>/dev/null || echo 'Not installed/running')" >> "$REPORT_FILE"
echo "AIDE: $(command -v aide &>/dev/null && echo 'Installed' || echo 'Not installed')" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "Security audit completed. Report saved to $REPORT_FILE"
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/security-config-audit.sh

# Add to crontab for weekly audits
echo "0 4 * * 0 /usr/local/bin/security-config-audit.sh" | sudo crontab -
```

## 5. Alerting Configuration

### 5.1 Alert Levels

#### Critical Alerts:
- Multiple failed authentication attempts
- Unauthorized network access
- Critical system vulnerabilities
- File integrity violations
- System compromise indicators

#### High Alerts:
- Suspicious user behavior
- High volume of errors
- Resource exhaustion
- Configuration changes
- Service disruptions

#### Medium Alerts:
- Warning conditions
- Rate limiting events
- Minor vulnerabilities
- System maintenance events

#### Low Alerts:
- Informational messages
- System status updates
- Routine maintenance

### 5.2 Alert Delivery Methods

#### Email Alerts:
```bash
# Configure email alerts
sudo nano /etc/mail.rc
```

```
set from=admin@yourdomain.com
set smtp=smtp.yourdomain.com
set smtp-auth=login
set smtp-auth-user=admin@yourdomain.com
set smtp-auth-password=yourpassword
```

#### Slack Alerts:
```bash
# Create Slack alert script
sudo nano /usr/local/bin/slack-alert.sh
```

```bash
#!/bin/bash
# Slack Alert Script

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
CHANNEL="#security-alerts"
USERNAME="AzureRAG-Security"

MESSAGE="$1"

curl -X POST -H 'Content-type: application/json' \
  --data "{\"channel\":\"$CHANNEL\",\"username\":\"$USERNAME\",\"text\":\"$MESSAGE\"}" \
  "$WEBHOOK_URL"
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/slack-alert.sh
```

### 5.3 Alert Response Procedures

#### Critical Alert Response:
1. Immediately investigate the alert
2. Isolate affected systems if necessary
3. Document findings
4. Implement corrective measures
5. Notify stakeholders
6. Update incident response plan

#### High Alert Response:
1. Investigate within 1 hour
2. Determine impact scope
3. Implement mitigations
4. Document actions taken
5. Schedule follow-up review

#### Medium Alert Response:
1. Investigate within 24 hours
2. Assess impact
3. Plan corrective actions
4. Document findings

#### Low Alert Response:
1. Review during routine maintenance
2. Address as part of regular updates
3. Document for future reference

## 6. Monitoring Dashboard

### 6.1 Kibana Dashboard Configuration

#### Create Monitoring Dashboard:
1. Access Kibana at `http://localhost:5601`
2. Navigate to "Analytics" > "Dashboard"
3. Create new dashboard with the following visualizations:

##### Security Overview Panel:
- Total security events (last 24 hours)
- Critical alerts count
- Authentication success/failure ratio
- Top 10 users by activity

##### System Health Panel:
- CPU and memory usage
- Disk space utilization
- Network traffic patterns
- Docker container status

##### Threat Intelligence Panel:
- Failed login attempts by IP
- Suspicious file access patterns
- Network connection attempts
- Vulnerability scan results

### 6.2 Custom Monitoring Scripts

#### Create System Health Monitor:
```bash
# Create system health monitor script
sudo nano /usr/local/bin/system-health-monitor.sh
```

```bash
#!/bin/bash
# System Health Monitor Script

HEALTH_REPORT="/var/log/azure-rag-system/health-report-$(date +%Y%m%d_%H%M%S).json"

# Collect system metrics
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
DOCKER_CONTAINERS=$(docker ps -q | wc -l)

# Create JSON report
cat > "$HEALTH_REPORT" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "system_metrics": {
    "cpu_usage_percent": $CPU_USAGE,
    "memory_usage_percent": $MEMORY_USAGE,
    "disk_usage_percent": $DISK_USAGE,
    "docker_containers_running": $DOCKER_CONTAINERS
  },
  "status": "$([ $(echo "$CPU_USAGE < 80" | bc -l) ] && [ $(echo "$MEMORY_USAGE < 80" | bc -l) ] && [ $DISK_USAGE -lt 80 ] && echo "healthy" || echo "degraded")"
}
EOF

# Send to Elasticsearch
curl -X POST "localhost:9200/system-health-$(date +%Y.%m.%d)/_doc/" \
  -H 'Content-Type: application/json' \
  -u "elastic:$ELASTIC_PASSWORD" \
  -d "@$HEALTH_REPORT" > /dev/null 2>&1

# Alert if system is degraded
if [ $(echo "$CPU_USAGE > 90" | bc -l) ] || [ $(echo "$MEMORY_USAGE > 90" | bc -l) ] || [ $DISK_USAGE -gt 90 ]; then
    echo "ALERT: System health degraded" | logger -t "AZURE-RAG-SYSTEM"
fi
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/system-health-monitor.sh

# Add to crontab for regular monitoring
echo "*/15 * * * * /usr/local/bin/system-health-monitor.sh" | sudo crontab -
```

## 7. Implementation Checklist

### 7.1 Log Aggregation
- [ ] Centralized logging directory created
- [ ] Docker log rotation configured
- [ ] Logstash configuration implemented
- [ ] Log file structure established
- [ ] Log rotation configured

### 7.2 Intrusion Detection
- [ ] OSSEC HIDS installed and configured
- [ ] Suricata NIDS installed and configured
- [ ] File integrity monitoring with AIDE
- [ ] Security event correlation rules implemented

### 7.3 Security Event Monitoring
- [ ] Elasticsearch security index templates created
- [ ] Security event correlation script implemented
- [ ] Alerting mechanisms configured
- [ ] Monitoring dashboard created

### 7.4 Automated Security Scanning
- [ ] Container vulnerability scanning implemented
- [ ] File integrity monitoring configured
- [ ] Security configuration auditing implemented
- [ ] Regular scanning schedules established

### 7.5 Alerting Configuration
- [ ] Alert levels defined
- [ ] Alert delivery methods configured
- [ ] Alert response procedures documented
- [ ] Monitoring dashboard implemented

## 8. Best Practices

### 8.1 Monitoring Best Practices
1. **Regular Review**: Review monitoring configurations monthly
2. **Alert Tuning**: Adjust alert thresholds based on actual usage patterns
3. **Log Retention**: Implement appropriate log retention policies
4. **Performance Monitoring**: Monitor the performance impact of monitoring tools
5. **Incident Response**: Maintain updated incident response procedures

### 8.2 Security Best Practices
1. **Principle of Least Privilege**: Ensure monitoring tools run with minimal privileges
2. **Encryption**: Encrypt logs in transit and at rest
3. **Access Control**: Restrict access to monitoring systems
4. **Regular Updates**: Keep monitoring tools updated with latest security patches
5. **Audit Trails**: Maintain audit trails of all monitoring activities

This monitoring and alerting configuration provides a comprehensive security monitoring solution for the Azure RAG System that builds upon the existing error monitoring capabilities while adding advanced security features.
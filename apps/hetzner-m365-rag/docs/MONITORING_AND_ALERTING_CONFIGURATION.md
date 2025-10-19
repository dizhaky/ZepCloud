# Monitoring and Alerting Configuration for M365 RAG System

## Overview

This document describes the monitoring and alerting configuration for the M365 RAG System to enhance security beyond the existing deployment. It includes log aggregation setup, intrusion detection system recommendations, security event monitoring, and automated security scanning to provide comprehensive security visibility and threat detection.

## 1. Log Aggregation Setup

### 1.1 Centralized Logging Architecture

The M365 RAG System will implement a centralized logging solution using the ELK stack (Elasticsearch, Logstash, Kibana) to aggregate logs from all system components.

### 1.2 Log Sources

#### Docker Container Logs
All Docker containers in the system generate logs that need to be collected:
- Elasticsearch service logs
- PostgreSQL database logs
- Redis cache logs
- MinIO object storage logs
- RAGFlow application logs
- Custom API service logs
- Nginx web server logs
- Prometheus monitoring logs
- Grafana visualization logs

#### System Logs
Critical system logs that need monitoring:
- Authentication logs (/var/log/auth.log)
- System logs (/var/log/syslog)
- Kernel logs (/var/log/kern.log)
- Firewall logs (/var/log/ufw.log)
- Application logs (/var/log/m365-rag-*.log)

### 1.3 Logstash Configuration

#### Create Logstash Pipeline Configuration
```bash
# Create Logstash configuration directory
sudo mkdir -p /data/m365-rag/config/logstash

# Create main Logstash configuration
sudo nano /data/m365-rag/config/logstash/logstash.yml
```

```yaml
# Logstash Configuration
http.host: "0.0.0.0"
path.config: /usr/share/logstash/pipeline
xpack.monitoring.enabled: false
```

#### Create Logstash Pipeline Configuration
```bash
# Create pipeline configuration
sudo nano /data/m365-rag/config/logstash/pipeline/m365-rag.conf
```

```ruby
input {
  # Docker container logs
  file {
    path => "/data/m365-rag/logs/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => "json"
    type => "docker"
  }
  
  # System logs
  file {
    path => "/var/log/auth.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    type => "auth"
  }
  
  # Syslog
  file {
    path => "/var/log/syslog"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    type => "syslog"
  }
  
  # Firewall logs
  file {
    path => "/var/log/ufw.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    type => "firewall"
  }
  
  # Fail2Ban logs
  file {
    path => "/var/log/fail2ban.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    type => "fail2ban"
  }
}

filter {
  # Parse Docker logs
  if [type] == "docker" {
    json {
      source => "message"
    }
    
    date {
      match => [ "time", "ISO8601" ]
      target => "@timestamp"
    }
  }
  
  # Parse authentication logs
  if [type] == "auth" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:timestamp} %{SYSLOGHOST:hostname} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:syslog_message}" }
    }
    
    # Detect failed login attempts
    if [syslog_message] =~ /Failed password/ {
      mutate {
        add_tag => [ "failed_login" ]
      }
    }
    
    # Detect successful logins
    if [syslog_message] =~ /Accepted/ {
      mutate {
        add_tag => [ "successful_login" ]
      }
    }
  }
  
  # Parse firewall logs
  if [type] == "firewall" {
    grok {
      match => { "message" => "%{SYSLOGTIMESTAMP:timestamp} %{SYSLOGHOST:hostname} %{DATA:program}\[%{POSINT:pid}\]: \[%{NUMBER:rule_id}\] %{WORD:action} %{WORD:protocol} src=%{IP:src_ip} dst=%{IP:dst_ip} .*" }
    }
    
    # Detect blocked connections
    if [action] == "BLOCK" {
      mutate {
        add_tag => [ "blocked_connection" ]
      }
    }
  }
  
  # Add geolocation data for IP addresses
  if [src_ip] {
    geoip {
      source => "src_ip"
      target => "geoip"
    }
  }
}

output {
  # Send to Elasticsearch
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    user => "${ELASTIC_USER:elastic}"
    password => "${ELASTIC_PASSWORD:changeme}"
    ssl => true
    ssl_certificate_verification => false
    index => "m365-rag-logs-%{+YYYY.MM.dd}"
  }
  
  # Send security events to separate index
  if "failed_login" in [tags] or "blocked_connection" in [tags] {
    elasticsearch {
      hosts => ["elasticsearch:9200"]
      user => "${ELASTIC_USER:elastic}"
      password => "${ELASTIC_PASSWORD:changeme}"
      ssl => true
      ssl_certificate_verification => false
      index => "m365-rag-security-%{+YYYY.MM.dd}"
    }
  }
}
```

### 1.4 Docker Compose Integration

#### Add Logstash Service to Docker Compose
```yaml
# Add to docker-compose.yml services section
  logstash:
    image: docker.elastic.co/logstash/logstash:8.15.0
    container_name: logstash
    environment:
      - ELASTIC_USER=elastic
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD:-changeme}
    volumes:
      - ./config/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./config/logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logs:/data/m365-rag/logs:ro
      - /var/log:/host/var/log:ro
    ports:
      - "5044:5044"
      - "9600:9600"
    networks:
      rag-network:
        ipv4_address: 172.28.0.40
    depends_on:
      - elasticsearch
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

#### Update Volume Configuration
```yaml
# Add to volumes section
  logstash-data:
```

### 1.5 Log Rotation and Retention

#### Configure Log Rotation
```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/m365-rag
```

```bash
# M365 RAG System log rotation
/data/m365-rag/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 deploy deploy
    postrotate
        docker kill --signal=USR1 m365-rag-api 2>/dev/null || true
    endscript
}

/var/log/m365-rag-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## 2. Intrusion Detection System Recommendations

### 2.1 Host-Based Intrusion Detection System (HIDS)

#### Install and Configure OSSEC/Wazuh
```bash
# Install Wazuh manager (on separate monitoring server or locally)
docker run -d --name wazuh-manager \
  --hostname wazuh-manager \
  -p 1514:1514/udp \
  -p 1515:1515/tcp \
  -p 55000:55000/tcp \
  -v wazuh-data:/var/ossec/data \
  -v /data/m365-rag/logs:/var/ossec/logs:rw \
  -v /data/m365-rag/etc:/var/ossec/etc:rw \
  wazuh/wazuh-manager:4.7.3
```

#### Configure Wazuh Agent
```bash
# Install Wazuh agent on the M365 RAG system
curl -so wazuh-agent.deb https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.7.3-1_amd64.deb
sudo dpkg -i wazuh-agent.deb

# Configure agent
sudo nano /var/ossec/etc/ossec.conf
```

```xml
<!-- Wazuh Agent Configuration -->
<ossec_config>
  <client>
    <server>
      <address>WAZUH_MANAGER_IP</address>
      <port>1514</port>
      <protocol>udp</protocol>
    </server>
    <config-profile>ubuntu, ubuntu20, ubuntu20.04</config-profile>
    <notify_time>10</notify_time>
    <time-reconnect>60</time-reconnect>
    <auto_restart>yes</auto_restart>
    <crypto_method>aes</crypto_method>
  </client>

  <!-- System Auditing -->
  <syscheck>
    <disabled>no</disabled>
    <frequency>43200</frequency>
    <scan_on_start>yes</scan_on_start>
    <directories check_all="yes">/etc,/usr/bin,/usr/sbin</directories>
    <directories check_all="yes">/bin,/sbin,/boot</directories>
    <ignore>/etc/mtab</ignore>
    <ignore>/etc/mnttab</ignore>
    <ignore>/etc/hosts.deny</ignore>
    <ignore>/etc/mail/statistics</ignore>
    <ignore>/etc/random-seed</ignore>
    <ignore>/etc/random.seed</ignore>
    <ignore>/etc/adjtime</ignore>
    <ignore>/etc/httpd/logs</ignore>
    <ignore>/etc/utmpx</ignore>
    <ignore>/etc/wtmpx</ignore>
    <ignore>/etc/cups/certs</ignore>
    <ignore>/etc/dumpdates</ignore>
    <ignore>/etc/svc/volatile</ignore>
  </syscheck>

  <!-- Rootkit Detection -->
  <rootcheck>
    <disabled>no</disabled>
    <rootkit_files>/var/ossec/etc/shared/rootkit_files.txt</rootkit_files>
    <rootkit_trojans>/var/ossec/etc/shared/rootkit_trojans.txt</rootkit_trojans>
    <system_audit>/var/ossec/etc/shared/system_audit_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_debian_linux_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_rhel_linux_rcl.txt</system_audit>
    <system_audit>/var/ossec/etc/shared/cis_rhel5_linux_rcl.txt</system_audit>
    <skip_nfs>yes</skip_nfs>
  </rootcheck>

  <!-- Security Configuration Assessment -->
  <sca>
    <enabled>yes</enabled>
    <scan_on_start>yes</scan_on_start>
    <interval>12h</interval>
    <skip_nfs>yes</skip_nfs>
  </sca>

  <!-- Log Collection -->
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
    <location>/var/log/ufw.log</location>
  </localfile>

  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/fail2ban.log</location>
  </localfile>
</ossec_config>
```

#### Start Wazuh Agent
```bash
# Enable and start Wazuh agent
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent

# Check agent status
sudo systemctl status wazuh-agent
```

### 2.2 Network-Based Intrusion Detection System (NIDS)

#### Install and Configure Suricata
```bash
# Install Suricata
sudo apt update
sudo apt install suricata

# Configure Suricata
sudo nano /etc/suricata/suricata.yaml
```

#### Configure Network Interface Monitoring
```yaml
# In suricata.yaml
af-packet:
  - interface: eth0
    threads: 2
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes
```

#### Configure Rules
```yaml
# Enable relevant rule sets
rule-files:
  - botcc.rules
  - ciarmy.rules
  - compromised.rules
  - drop.rules
  - dshield.rules
  - emerging-attack_response.rules
  - emerging-chat.rules
  - emerging-current_events.rules
  - emerging-dns.rules
  - emerging-dos.rules
  - emerging-exploit.rules
  - emerging-ftp.rules
  - emerging-games.rules
  - emerging-icmp_info.rules
  - emerging-icmp.rules
  - emerging-imap.rules
  - emerging-malware.rules
  - emerging-misc.rules
  - emerging-mobile_malware.rules
  - emerging-netbios.rules
  - emerging-p2p.rules
  - emerging-policy.rules
  - emerging-pop3.rules
  - emerging-rpc.rules
  - emerging-scada.rules
  - emerging-scan.rules
  - emerging-shellcode.rules
  - emerging-smtp.rules
  - emerging-snmp.rules
  - emerging-sql.rules
  - emerging-telnet.rules
  - emerging-tftp.rules
  - emerging-trojan.rules
  - emerging-user_agents.rules
  - emerging-voip.rules
  - emerging-web_client.rules
  - emerging-web_server.rules
  - emerging-web_specific_apps.rules
  - emerging-worm.rules
  - tor.rules
```

#### Start Suricata
```bash
# Enable and start Suricata
sudo systemctl enable suricata
sudo systemctl start suricata

# Update rules
sudo suricata-update

# Test configuration
sudo suricata -T -c /etc/suricata/suricata.yaml
```

## 3. Security Event Monitoring

### 3.1 Elasticsearch Security Index Configuration

#### Create Security Index Template
```bash
# Create security index template
curl -X PUT "localhost:9200/_index_template/m365-rag-security" \
  -u "elastic:$ELASTIC_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "index_patterns": ["m365-rag-security-*"],
    "template": {
      "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "refresh_interval": "30s"
      },
      "mappings": {
        "properties": {
          "@timestamp": {
            "type": "date"
          },
          "event_type": {
            "type": "keyword"
          },
          "source_ip": {
            "type": "ip"
          },
          "destination_ip": {
            "type": "ip"
          },
          "user": {
            "type": "keyword"
          },
          "message": {
            "type": "text"
          },
          "severity": {
            "type": "keyword"
          },
          "geoip": {
            "properties": {
              "location": {
                "type": "geo_point"
              },
              "country_name": {
                "type": "keyword"
              },
              "city_name": {
                "type": "keyword"
              }
            }
          }
        }
      }
    }
  }'
```

### 3.2 Security Event Correlation Rules

#### Create Watcher Alerts in Elasticsearch
```bash
# Create alert for multiple failed login attempts
curl -X PUT "localhost:9200/_watcher/watch/failed_login_alert" \
  -u "elastic:$ELASTIC_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "trigger": {
      "schedule": {
        "interval": "1m"
      }
    },
    "input": {
      "search": {
        "request": {
          "search_type": "query_then_fetch",
          "indices": ["m365-rag-security-*"],
          "body": {
            "size": 0,
            "query": {
              "bool": {
                "must": [
                  {
                    "range": {
                      "@timestamp": {
                        "gte": "now-5m/m"
                      }
                    }
                  },
                  {
                    "term": {
                      "tags": "failed_login"
                    }
                  }
                ]
              }
            },
            "aggs": {
              "failed_logins": {
                "terms": {
                  "field": "user.keyword",
                  "size": 10
                },
                "aggs": {
                  "ip_addresses": {
                    "terms": {
                      "field": "src_ip.keyword",
                      "size": 10
                    }
                  }
                }
              }
            }
          }
        }
      }
    },
    "condition": {
      "script": {
        "source": "ctx.payload.aggregations.failed_logins.buckets.stream().anyMatch(bucket -> bucket.doc_count > 5)"
      }
    },
    "actions": {
      "send_email": {
        "email": {
          "to": "security@m365-rag.local",
          "subject": "Multiple Failed Login Attempts Detected",
          "body": "Multiple failed login attempts detected in the last 5 minutes. Please investigate."
        }
      }
    }
  }'
```

#### Create Alert for Suspicious Network Activity
```bash
# Create alert for blocked firewall connections
curl -X PUT "localhost:9200/_watcher/watch/blocked_connections_alert" \
  -u "elastic:$ELASTIC_PASSWORD" \
  -H 'Content-Type: application/json' \
  -d '{
    "trigger": {
      "schedule": {
        "interval": "1m"
      }
    },
    "input": {
      "search": {
        "request": {
          "search_type": "query_then_fetch",
          "indices": ["m365-rag-security-*"],
          "body": {
            "size": 0,
            "query": {
              "bool": {
                "must": [
                  {
                    "range": {
                      "@timestamp": {
                        "gte": "now-10m/m"
                      }
                    }
                  },
                  {
                    "term": {
                      "tags": "blocked_connection"
                    }
                  }
                ]
              }
            },
            "aggs": {
              "blocked_ips": {
                "terms": {
                  "field": "src_ip.keyword",
                  "size": 20
                }
              }
            }
          }
        }
      }
    },
    "condition": {
      "script": {
        "source": "ctx.payload.aggregations.blocked_ips.buckets.stream().anyMatch(bucket -> bucket.doc_count > 10)"
      }
    },
    "actions": {
      "send_email": {
        "email": {
          "to": "security@m365-rag.local",
          "subject": "High Volume of Blocked Connections Detected",
          "body": "A high volume of blocked connections has been detected. Please investigate potential scanning or attack activity."
        }
      }
    }
  }'
```

## 4. Automated Security Scanning

### 4.1 Vulnerability Scanning

#### Implement Daily Vulnerability Scanning
```bash
# Create vulnerability scanning script
sudo nano /usr/local/bin/vulnerability-scan.sh
```

```bash
#!/bin/bash
# M365 RAG System Vulnerability Scanner

# Scan Docker images
echo "Scanning Docker images for vulnerabilities..."
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest \
  --severity HIGH,CRITICAL \
  --format json \
  --output /tmp/trivy-results.json \
  --quiet \
  image \
  infiniflow/ragflow:latest

# Scan system packages
echo "Scanning system packages for vulnerabilities..."
docker run --rm \
  -v /:/host:ro \
  aquasec/trivy:latest \
  --severity HIGH,CRITICAL \
  --format json \
  --output /tmp/trivy-system-results.json \
  --quiet \
  filesystem \
  /host

# Check results and alert if critical vulnerabilities found
CRITICAL_COUNT=$(jq '[.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL")] | length' /tmp/trivy-results.json)
HIGH_COUNT=$(jq '[.Results[].Vulnerabilities[] | select(.Severity=="HIGH")] | length' /tmp/trivy-results.json)

if [ "$CRITICAL_COUNT" -gt 0 ] || [ "$HIGH_COUNT" -gt 5 ]; then
  echo "Critical or high vulnerabilities detected:"
  echo "Critical: $CRITICAL_COUNT"
  echo "High: $HIGH_COUNT"
  
  # Send alert (implement your preferred notification method)
  # Example: send email, Slack notification, etc.
  echo "Vulnerability scan detected critical issues. Please check /tmp/trivy-results.json" | mail -s "Vulnerability Alert" security@m365-rag.local
fi

echo "Vulnerability scan completed."
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/vulnerability-scan.sh

# Add to crontab for daily scanning
echo "0 3 * * * /usr/local/bin/vulnerability-scan.sh >> /var/log/vulnerability-scan.log 2>&1" | sudo crontab -
```

### 4.2 Configuration Auditing

#### Implement CIS Benchmark Scanning
```bash
# Create CIS benchmark scanning script
sudo nano /usr/local/bin/cis-benchmark-scan.sh
```

```bash
#!/bin/bash
# M365 RAG System CIS Benchmark Scanner

# Run Docker Bench Security
echo "Running Docker Bench Security..."
docker run --rm \
  --net host \
  --pid host \
  --userns host \
  --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/lib/systemd:/usr/lib/systemd \
  -v /etc:/etc \
  --label docker_bench_security \
  docker/docker-bench-security > /tmp/docker-bench-results.txt

# Run Lynis security audit
echo "Running Lynis security audit..."
sudo lynis audit system --quick > /tmp/lynis-results.txt

# Check for critical findings
if grep -q "Critical" /tmp/docker-bench-results.txt || grep -q "Critical" /tmp/lynis-results.txt; then
  echo "Critical security issues detected in configuration audit."
  
  # Send alert
  echo "CIS benchmark scan detected critical configuration issues. Please check audit results." | mail -s "Configuration Audit Alert" security@m365-rag.local
fi

echo "CIS benchmark scan completed."
```

```bash
# Install Lynis
sudo apt install lynis

# Make script executable
sudo chmod +x /usr/local/bin/cis-benchmark-scan.sh

# Add to crontab for weekly scanning
echo "0 4 * * 0 /usr/local/bin/cis-benchmark-scan.sh >> /var/log/cis-benchmark-scan.log 2>&1" | sudo crontab -
```

### 4.3 File Integrity Monitoring

#### Implement AIDE for File Integrity Monitoring
```bash
# Install AIDE
sudo apt install aide

# Initialize AIDE database
sudo aideinit

# Configure AIDE
sudo nano /etc/aide/aide.conf
```

#### Configure AIDE Rules
```bash
# In /etc/aide/aide.conf
# Define rules
AllRules = p+i+n+u+g+s+m+c+acl+selinux+xattrs+sha512

# Define monitored directories
/etc AllRules
/bin AllRules
/sbin AllRules
/usr/bin AllRules
/usr/sbin AllRules
/data/m365-rag AllRules
```

#### Create AIDE Check Script
```bash
# Create AIDE check script
sudo nano /usr/local/bin/aide-check.sh
```

```bash
#!/bin/bash
# M365 RAG System File Integrity Check

echo "Running AIDE file integrity check..."
sudo aide --check > /tmp/aide-results.txt 2>&1

# Check for changes
if grep -q "Changed" /tmp/aide-results.txt || grep -q "Added" /tmp/aide-results.txt || grep -q "Removed" /tmp/aide-results.txt; then
  echo "File integrity violations detected:"
  grep -E "(Changed|Added|Removed)" /tmp/aide-results.txt
  
  # Send alert
  echo "File integrity violations detected. Please check /tmp/aide-results.txt" | mail -s "File Integrity Alert" security@m365-rag.local
else
  echo "No file integrity violations detected."
fi

echo "AIDE check completed."
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/aide-check.sh

# Add to crontab for daily checking
echo "0 5 * * * /usr/local/bin/aide-check.sh >> /var/log/aide-check.log 2>&1" | sudo crontab -
```

## 5. Monitoring Dashboard Configuration

### 5.1 Kibana Security Dashboard

#### Create Security Dashboard in Kibana
1. Access Kibana at `http://YOUR_SERVER_IP:5601`
2. Navigate to Analytics > Dashboard
3. Create a new dashboard named "M365 RAG Security Overview"
4. Add visualizations for:
   - Failed login attempts over time
   - Blocked firewall connections by IP
   - Security events by type
   - System resource usage during security events
   - Geolocation of suspicious connections

### 5.2 Grafana Security Dashboard

#### Create Grafana Dashboard for Security Metrics
```bash
# Create Grafana dashboard configuration
sudo nano /data/m365-rag/config/grafana/dashboards/security-dashboard.json
```

```json
{
  "dashboard": {
    "id": null,
    "title": "M365 RAG Security Dashboard",
    "tags": ["security", "monitoring"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "type": "graph",
        "title": "Failed Login Attempts",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "rate(auth_failed_logins[5m])",
            "legendFormat": "Failed Logins"
          }
        ],
        "xaxis": {
          "mode": "time"
        },
        "yaxes": [
          {
            "format": "short",
            "label": "Attempts per second"
          }
        ]
      },
      {
        "id": 2,
        "type": "table",
        "title": "Top Blocked IPs",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "topk(10, sum by (src_ip) (firewall_blocked_connections))",
            "legendFormat": "{{src_ip}}"
          }
        ],
        "columns": [
          {"text": "Source IP", "value": "src_ip"},
          {"text": "Blocked Count", "value": "Value"}
        ]
      },
      {
        "id": 3,
        "type": "stat",
        "title": "Critical Vulnerabilities",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "vulnerability_critical_count",
            "legendFormat": "Critical"
          }
        ],
        "options": {
          "colorMode": "value",
          "graphMode": "none",
          "justifyMode": "auto",
          "orientation": "horizontal",
          "reduceOptions": {
            "calcs": ["lastNotNull"],
            "fields": "",
            "values": false
          }
        }
      }
    ]
  }
}
```

## 6. Alerting Configuration

### 6.1 Email Alerting Setup

#### Configure Email Notifications
```bash
# Create email configuration for alerts
sudo nano /etc/ssmtp/ssmtp.conf
```

```bash
# SSMTP Configuration
root=security@m365-rag.local
mailhub=smtp.your-email-provider.com:587
AuthUser=security@m365-rag.local
AuthPass=your-email-password
UseSTARTTLS=YES
```

### 6.2 Slack Alerting Setup

#### Create Slack Webhook Integration
```bash
# Create Slack alert script
sudo nano /usr/local/bin/slack-alert.sh
```

```bash
#!/bin/bash
# Slack Alert Script

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
MESSAGE="$1"

curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$MESSAGE\"}" \
  $WEBHOOK_URL
```

```bash
# Make script executable
sudo chmod +x /usr/local/bin/slack-alert.sh
```

## 7. Implementation Checklist

### 7.1 Log Aggregation
- [ ] Logstash service added to docker-compose.yml
- [ ] Logstash pipeline configuration created
- [ ] Log rotation configured
- [ ] Container logs properly routed to Logstash

### 7.2 Intrusion Detection
- [ ] Wazuh agent installed and configured
- [ ] Suricata installed and configured
- [ ] Network interface monitoring enabled
- [ ] Security rules updated and active

### 7.3 Security Event Monitoring
- [ ] Elasticsearch security index template created
- [ ] Watcher alerts configured for failed logins
- [ ] Watcher alerts configured for blocked connections
- [ ] Kibana security dashboard created

### 7.4 Automated Security Scanning
- [ ] Daily vulnerability scanning implemented
- [ ] Weekly CIS benchmark scanning implemented
- [ ] Daily file integrity monitoring implemented
- [ ] Alerting configured for critical findings

### 7.5 Monitoring Dashboards
- [ ] Kibana security dashboard configured
- [ ] Grafana security dashboard configured
- [ ] Alerting channels configured (email, Slack)

## 8. Testing and Validation

### 8.1 Test Procedures

#### Log Aggregation Testing
1. Verify Logstash is receiving logs from all sources
2. Check Elasticsearch indices for proper log data
3. Validate log parsing and field extraction
4. Test log rotation and retention policies

#### Intrusion Detection Testing
1. Simulate failed login attempts to test HIDS alerts
2. Generate network traffic to test NIDS detection
3. Verify alert notifications are working
4. Check false positive rates and adjust rules as needed

#### Security Event Monitoring Testing
1. Trigger failed login scenarios to test alerts
2. Simulate blocked connections to test firewall alerts
3. Verify dashboard visualizations are updating correctly
4. Test alert escalation procedures

#### Automated Security Scanning Testing
1. Run vulnerability scans manually to verify functionality
2. Check CIS benchmark scan results
3. Verify file integrity monitoring detects changes
4. Test alert notifications for critical findings

This monitoring and alerting configuration provides comprehensive security visibility for the M365 RAG System, enabling rapid detection and response to security threats while maintaining detailed audit trails for compliance purposes.
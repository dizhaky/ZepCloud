# Changelog

All notable changes to the M365 RAG System (Hetzner deployment) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-10-18

### Added

#### Infrastructure
- Complete Docker Compose orchestration for all services
- Elasticsearch 8.15.0 with vector search support
- PostgreSQL 16 with pgvector extension
- Redis 7 for caching layer
- MinIO for S3-compatible object storage
- RAGFlow for production UI and workflows
- Nginx reverse proxy with SSL support
- Prometheus + Grafana monitoring stack

#### Application
- FastAPI-based API server with async support
- RAG-Anything integration for multimodal processing
- Elasticsearch adapter replacing Azure AI Search
- MinIO adapter replacing Azure Blob Storage
- Health check endpoints
- Search API with hybrid retrieval (vector + BM25)
- Document ingestion pipeline
- Background task processing

#### M365 Integration
- M365 authentication modules (interactive, delegated, app)
- Support for multiple authentication methods
- SharePoint connector (ready for adaptation)
- OneDrive connector (ready for adaptation)
- Teams connector (ready for adaptation)
- Outlook connector (ready for adaptation)
- Calendar and Contacts indexing

#### Security
- LUKS disk encryption support
- UFW firewall configuration
- Fail2ban brute-force protection
- SSL/TLS with Let's Encrypt
- JWT-based API authentication
- Secure password generation
- Environment variable management

#### Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Elasticsearch exporter for cluster metrics
- System health monitoring
- Alert configuration for critical events
- Performance metrics tracking

#### Backup & Recovery
- Automated daily backup script
- Elasticsearch snapshot management
- PostgreSQL dump automation
- Configuration backup
- 30-day retention policy
- Restore script with verification
- Disaster recovery procedures

#### Documentation
- Comprehensive README
- Implementation guide
- Architecture specification
- Deployment checklist
- API documentation
- Troubleshooting guide
- Security best practices

#### Scripts
- Automated deployment script
- Backup and restore scripts
- Database initialization script
- Service management utilities

#### Configuration
- Elasticsearch configuration
- Nginx configuration
- Prometheus configuration
- Grafana datasources and dashboards
- Docker Compose service definitions
- Environment variable templates

### Security Considerations

- All secrets managed via environment variables
- Passwords generated with cryptographically secure random generators
- Disk encryption enabled for sensitive data
- Network segmentation via Docker networks
- Minimal port exposure (only 22, 80, 443)
- Regular security updates via unattended-upgrades

### Performance Targets

- Query latency p50: < 500ms
- Query latency p95: < 2s
- Document indexing: 100 docs/min
- Concurrent users: 50+
- System uptime: 99.5%
- Total RAM usage: ~38GB (90GB available)

### Cost Analysis

- **Infrastructure:** $108/month (Hetzner AX52)
- **API costs:** $50-500/month (OpenAI)
- **Total:** $158-608/month
- **Savings vs Azure:** $8,000-14,000/year

---

## [Unreleased]

### Planned Features

- [ ] Advanced RAG-Anything features (knowledge graphs)
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Additional M365 sources (Planner, Forms)
- [ ] Multi-language support
- [ ] Advanced security features (2FA, SSO)
- [ ] Horizontal scaling support
- [ ] Kubernetes deployment option
- [ ] Advanced caching strategies

### Known Issues

- None currently tracked

### Deprecations

- None

---

## Migration Notes

### From Azure-based System

If migrating from the existing Azure-based setup:

1. **Export data from Azure AI Search**
   - Use Azure portal or SDK to export documents
   - Save to JSON or CSV format

2. **Migrate to Elasticsearch**
   - Use bulk indexing API
   - Adapt index schemas
   - Verify all documents indexed

3. **Move files from Azure Blob to MinIO**
   - Download blobs locally
   - Upload to MinIO
   - Update references

4. **Update M365 connectors**
   - Replace Azure SDK calls with new adapters
   - Test authentication
   - Verify sync functionality

5. **Configure monitoring**
   - Migrate alerts from Azure Monitor to Prometheus
   - Create equivalent Grafana dashboards

6. **Test thoroughly**
   - Verify all functionality
   - Run load tests
   - Validate data integrity

---

## Support

For questions, issues, or feature requests:

- **Documentation:** See `docs/` directory
- **Issues:** GitHub Issues
- **Community:** Discord (TBD)
- **Email:** support@example.com

---

## Contributors

- Initial implementation: Dan Izhaky

---

## License

[Add license information]


# Security Policy

## Supported Versions

We actively maintain security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in ZepCloud, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to prevent exploitation.

### 2. **Email Security Report**
Send an email to: [security@zepcloud.dev](mailto:security@zepcloud.dev)

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information

### 3. **Response Timeline**
- **Acknowledgment**: Within 24 hours
- **Initial Assessment**: Within 72 hours  
- **Resolution**: Within 30 days (depending on severity)

### 4. **What to Expect**
- We will investigate the report promptly
- We will keep you informed of our progress
- We will work with you to validate and address the vulnerability
- We will credit you in our security advisories (unless you prefer to remain anonymous)

## Security Best Practices

### For Contributors
- Always use the latest versions of dependencies
- Run security scans before submitting PRs
- Follow secure coding practices
- Never commit secrets or credentials

### For Users
- Keep your dependencies updated
- Use environment variables for sensitive configuration
- Regularly review and rotate API keys
- Monitor for security advisories

## Dependabot Configuration

This repository uses Dependabot for automated security updates:
- **Weekly scans** for new vulnerabilities
- **Automatic PRs** for security updates
- **Grouped updates** by dependency type
- **Review process** for all security changes

## Security Features

- ✅ **Dependabot**: Automated dependency updates
- ✅ **Secret Scanning**: Prevents credential leaks
- ✅ **Code Scanning**: Identifies security issues
- ✅ **Dependency Review**: Checks for vulnerable dependencies

## Contact

For security-related questions or concerns:
- **Email**: [security@zepcloud.dev](mailto:security@zepcloud.dev)
- **GitHub**: Create a private security advisory
- **Discord**: [ZepCloud Security Channel](https://discord.gg/zepcloud)

---

**Thank you for helping keep ZepCloud secure!** 🛡️

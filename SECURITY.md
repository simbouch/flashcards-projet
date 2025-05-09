# Security Policy

## Supported Versions

We provide security updates for the following versions of the Flashcards Application:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of our application seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly** until it has been addressed by our team.
2. Email your findings to security@flashcards-app.com.
3. Include detailed information about the vulnerability, including:
   - The type of vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (if available)

## What to Expect

- We will acknowledge receipt of your vulnerability report within 48 hours.
- We will provide an initial assessment of the report within 5 business days.
- We aim to address critical vulnerabilities within 30 days.
- We will keep you informed about our progress throughout the process.
- After the vulnerability has been fixed, we will publicly acknowledge your contribution (unless you prefer to remain anonymous).

## Security Measures

The Flashcards Application implements the following security measures:

### Authentication and Authorization

- Password hashing using bcrypt with appropriate work factors
- JWT-based authentication with short-lived tokens
- Role-based access control
- CSRF protection

### Data Protection

- HTTPS for all communications
- Encryption of sensitive data at rest
- Input validation and sanitization
- Parameterized queries to prevent SQL injection

### Infrastructure Security

- Regular security updates for all dependencies
- Containerized services with minimal privileges
- Network segmentation
- Regular security scanning and auditing

### Development Practices

- Secure code review process
- Automated security testing
- Dependency vulnerability scanning
- Regular security training for developers

## Responsible Disclosure

We are committed to working with security researchers and the open-source community to identify and address security vulnerabilities. We promise not to take legal action against researchers who:

- Make a good faith effort to avoid privacy violations, destruction of data, and interruption or degradation of our services
- Only interact with accounts they own or with explicit permission of the account holder
- Do not exploit a security issue for purposes other than verification
- Report vulnerabilities directly to us and give us reasonable time to respond before disclosing to the public

Thank you for helping keep the Flashcards Application and its users safe!

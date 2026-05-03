# Security Policy

## Supported Versions

This project is coursework software and currently supports the latest code on the `main` branch.

## Reporting a Vulnerability

Do not open a public issue for secrets, credential leaks, or exploitable security vulnerabilities.

Report security concerns privately to the repository owner, or use GitHub private vulnerability reporting if it is enabled for this repository.

## Secret Handling

- Do not commit `.env` files, API keys, access tokens, private certificates, or database credentials.
- Store local secrets in `.env` files that are ignored by Git.
- Store production secrets in the hosting provider or GitHub Actions secret manager.
- Rotate any secret immediately if it has been committed or shared.

## Recommended GitHub Security Settings

Enable these in GitHub repository settings:

- Dependabot alerts.
- Dependabot security updates.
- Secret protection.
- Push protection.
- Code scanning with CodeQL.

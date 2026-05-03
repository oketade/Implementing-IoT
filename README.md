# RDI Smart CV Platform

[![CodeQL](https://github.com/oketade/Implementing-IoT/actions/workflows/codeql.yml/badge.svg)](https://github.com/oketade/Implementing-IoT/actions/workflows/codeql.yml)
[![CI](https://github.com/oketade/Implementing-IoT/actions/workflows/ci.yml/badge.svg)](https://github.com/oketade/Implementing-IoT/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-not%20configured-lightgrey.svg)](#testing)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](project/school_RDI_Platform/frontend/package.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Issues](https://img.shields.io/github/issues/oketade/Implementing-IoT)](https://github.com/oketade/Implementing-IoT/issues)

RDI Smart CV Platform is a full-stack web application for uploading, parsing, enhancing, and managing CV data. It combines a React frontend with a FastAPI backend so students, job seekers, and career support teams can turn CV documents into structured profiles and improved resume content.

## Overview

The project helps users convert CV files into editable profile data, improve CV content with AI assistance, and prepare a cleaner candidate profile for applications or institutional review.

Target users include:

- Students preparing professional CVs.
- Career service teams reviewing applicant profiles.
- Developers learning how to connect a React frontend, FastAPI backend, SQL database, and AI services.

## Features

- CV upload and parsing workflow.
- Editable profile and CV builder pages.
- AI/NLP-powered CV parsing for names, skills, education, experience, and contact details.
- AI enhancement panel for improving resume content.
- AI-assisted skill suggestions based on parsed CV content.
- Profile strength calculation.
- Company modal for application-related profile review.
- REST API built with FastAPI.
- Database schema for profile and CV data.
- Health check endpoint for backend monitoring.

## Getting Started

### Prerequisites

- Python 3.10 or later.
- Node.js 18 or later.
- npm.
- Git.
- Optional: PostgreSQL if you configure the backend for a PostgreSQL database.

### Installation

Clone the repository:

```bash
git clone https://github.com/oketade/Implementing-IoT.git
cd Implementing-IoT
```

Install backend dependencies:

```bash
cd project/school_RDI_Platform/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd ../frontend
npm install
```

### Configuration

Create a backend `.env` file in `project/school_RDI_Platform/backend` if your local setup needs API keys or database settings:

```env
FRONTEND_URL=http://localhost:3000
DATABASE_URL=sqlite:///./rdi_smart_cv.db
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

Do not commit `.env` files or real API keys.

### Quick Start

Start the backend:

```bash
cd project/school_RDI_Platform/backend
uvicorn main:app --reload
```

Start the frontend in a second terminal:

```bash
cd project/school_RDI_Platform/frontend
npm start
```

Open the frontend at `http://localhost:3000`. The backend health endpoint is available at `http://localhost:8000/health`.

## Usage

Common workflow:

1. Upload a CV document.
2. Review parsed CV data.
3. Edit missing or incorrect profile details.
4. Use AI enhancement tools to improve CV sections.
5. Save the profile and review the generated profile page.

## Project Structure

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── SECURITY.md
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── ci.yml
│       └── codeql.yml
├── Machine learning/
└── project/
    └── school_RDI_Platform/
        ├── backend/
        │   ├── main.py
        │   ├── database.py
        │   ├── models.py
        │   ├── schemas.py
        │   ├── requirements.txt
        │   ├── routers/
        │   └── services/
        ├── frontend/
        │   ├── package.json
        │   ├── public/
        │   └── src/
        └── schema.sql
```

## Tech Stack

- Frontend: React, JavaScript, CSS.
- Backend: FastAPI, Python, SQLAlchemy, Pydantic.
- Database: SQL schema included; backend can be configured for local or hosted databases.
- AI/NLP: spaCy, OpenAI API, Anthropic API.
- Document processing: pdfplumber, PyMuPDF, python-docx, pytesseract, Pillow.
- Security automation: Dependabot and CodeQL configuration.

## Machine Learning / AI Component

The platform includes an applied AI/NLP component for CV parsing and enhancement. It uses spaCy natural language processing to extract structured information such as names, locations, skills, education, and experience from CV text. It also supports OpenAI and Anthropic APIs for AI-assisted CV content improvement and skill suggestions.

## Architecture Overview

The React app provides the user interface for uploading CVs, editing profile data, and viewing saved profile information. The FastAPI backend exposes API routes for CV processing, profile management, and AI-assisted improvements. Backend services handle parsing, PDF generation, AI requests, and document extraction. SQLAlchemy models define the application data layer.

## Testing

Frontend tests can be run with:

```bash
cd project/school_RDI_Platform/frontend
npm test
```

Backend test coverage is not yet fully implemented. A recommended next step is to add `pytest` tests for API routes, CV parsing services, and database behavior.

## CI/CD and Deployment

This repository includes GitHub Actions workflows for CI checks and CodeQL code scanning. The CI workflow installs frontend and backend dependencies, builds the React app, runs frontend tests in CI mode, and verifies Python source files compile.

Recommended deployment approach:

- Deploy the frontend as a static React build.
- Deploy the FastAPI backend with Uvicorn or Gunicorn/Uvicorn workers.
- Store secrets in the deployment platform secret manager, not in the repository.
- Use a managed PostgreSQL database for production.

## Roadmap

- Add backend unit and integration tests.
- Add a full GitHub Actions CI workflow for frontend and backend checks.
- Add database migrations with Alembic.
- Improve error handling around document parsing and AI provider failures.
- Add deployment documentation for a chosen hosting platform.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make focused changes with clear commit messages.
4. Run available tests before opening a pull request.
5. Open a pull request that explains the problem, solution, and testing performed.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Security

Security policy details are in [SECURITY.md](SECURITY.md).

For GitHub repository security, enable these features in repository settings:

- Dependabot alerts.
- Secret protection.
- Push protection.
- Code scanning with CodeQL.

## Acknowledgments and Contact

This project was created as part of an Implementing IoT coursework repository. For questions or issues, open a GitHub issue in this repository.

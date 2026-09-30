# RDI Smart CV Platform

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](project/RDI_SMART_CV_Platform/frontend/package.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**RDI Smart CV Platform** is a full-stack web application that turns a CV document into a structured, editable profile. A user uploads a CV (PDF, DOCX or TXT), the backend extracts and parses the text with *natural language processing*, and the user can then review the result, improve it with AI and export a clean CV.

---

## Table of Contents

1. [Purpose](#purpose)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Dependencies](#dependencies)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Maintainer](#maintainer)
9. [License](#license)

## Purpose

Writing and updating a CV by hand is slow, and CVs come in many different layouts. The purpose of this project is to:

- **Read** a CV in any common file format.
- **Extract** the important information (name, contact details, skills, education and work experience) automatically.
- **Improve** the wording of CV sections with AI assistance.
- **Store** the result as a profile that can be edited and exported as a PDF.

Target users are students preparing professional CVs, career service teams reviewing applicant profiles, and developers learning how a React frontend, a FastAPI backend, a SQL database and AI services work together.

## Features

- CV upload and automatic parsing
- Editable profile and CV builder pages
- AI text enhancement with a selectable tone
- AI skill suggestions based on the parsed CV
- Profile strength score
- PDF export of the finished CV
- REST API with a `/health` endpoint for monitoring

## Prerequisites

Install the following software before setting up the project:

| Software | Version | Needed for |
|----------|---------|------------|
| [Python](https://www.python.org/downloads/) | 3.10 or later | Backend API |
| [Node.js](https://nodejs.org/) and npm | 18 or later | Frontend |
| [Git](https://git-scm.com/) | any recent | Cloning the repository |
| [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) | 5.x | Reading scanned (image-based) CVs |
| PostgreSQL | 14 or later | *Optional*, SQLite is used if no database is configured |

You also need an **OpenAI** or **Anthropic** API key if you want to use the AI enhancement features.

## Dependencies

The project relies on the following external libraries. They are installed automatically in the [Installation](#installation) step.

### Backend (Python, `requirements.txt`)

| Library | Purpose |
|---------|---------|
| `fastapi` | Web framework for the REST API |
| `uvicorn` | ASGI server that runs the API |
| `sqlalchemy` | Database models and queries |
| `pydantic` | Request and response validation |
| `pdfplumber`, `pymupdf` | Extracting text from PDF files |
| `python-docx` | Extracting text from Word files |
| `pytesseract`, `Pillow` | OCR for scanned CVs |
| `spacy` | Natural language processing (named entity recognition) |
| `openai`, `anthropic` | AI text enhancement and parsing |
| `weasyprint` | Generating the exported PDF |
| `python-dotenv` | Loading settings from a `.env` file |

### Frontend (JavaScript, `package.json`)

| Library | Purpose |
|---------|---------|
| `react`, `react-dom` | User interface |
| `react-scripts` | Development server, build and test tooling |

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/oketade/Implementing-IoT.git
   cd Implementing-IoT
   ```

2. Create a virtual environment and install the backend dependencies:

   ```bash
   cd project/RDI_SMART_CV_Platform/backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

   > **Note:** On macOS or Linux, activate the virtual environment with `source venv/bin/activate` instead.

3. Create a `.env` file in the `backend` folder:

   ```env
   DATABASE_URL=sqlite:///./rdi_smart_cv.db
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   FRONTEND_URL=http://localhost:3000
   ```

   > **Warning:** Never commit the `.env` file or real API keys to Git.

4. Install the frontend dependencies:

   ```bash
   cd ../frontend
   npm install
   ```

## Usage

### Starting the application

Start the backend in one terminal:

```bash
cd project/RDI_SMART_CV_Platform/backend
uvicorn main:app --reload
```

Start the frontend in a second terminal:

```bash
cd project/RDI_SMART_CV_Platform/frontend
npm start
```

Then open <http://localhost:3000> in a browser. The interactive API documentation is available at <http://localhost:8000/docs>.

### Example 1: Using the web interface

1. Upload a CV file on the start page.
2. Wait while the CV is parsed.
3. Check the extracted details in the **CV Builder** and fix anything that is missing.
4. Click **Enhance with AI** to improve a section, for example your profile summary.
5. Save the profile, open **My Profile** and click **Export PDF**.

### Example 2: Using the API directly

Check that the backend is running:

```bash
curl http://localhost:8000/health
```

Response:

```json
{"status": "ok", "service": "RDI Smart CV API"}
```

Upload and parse a CV:

```bash
curl -X POST http://localhost:8000/upload-cv -F "file=@my_cv.pdf"
```

Improve a piece of CV text:

```bash
curl -X POST http://localhost:8000/enhance-text \
  -H "Content-Type: application/json" \
  -d '{"text": "I made websites for customers.", "tone": "professional"}'
```

### Main API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Checks that the API is running |
| `POST` | `/upload-cv` | Uploads a CV file and returns the parsed data |
| `POST` | `/parse-cv` | Parses CV text that has been pasted in |
| `POST` | `/enhance-text` | Rewrites CV text with AI |
| `POST` | `/suggest-skills` | Suggests skills missing from the CV |
| `POST` | `/save-profile` | Creates or updates a profile |
| `GET` | `/profile/{profile_id}` | Returns a saved profile |
| `POST` | `/generate-pdf` | Exports a profile as a PDF |

## Project Structure

```text
project/RDI_SMART_CV_Platform/
├── backend/
│   ├── main.py            # FastAPI application entry point
│   ├── database.py        # Database connection
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── requirements.txt   # Python dependencies
│   ├── routers/           # API routes (cv, profile, ai)
│   └── services/          # Parsing, AI and PDF logic
├── frontend/
│   ├── package.json       # JavaScript dependencies
│   ├── public/
│   └── src/               # React pages and components
└── schema.sql             # Database schema
```

## Maintainer

This project is maintained by **Peter Adedayo Oketade** ([@oketade](https://github.com/oketade)).

Bug reports and feature requests are welcome in the [GitHub issue tracker](https://github.com/oketade/Implementing-IoT/issues). Security issues should be reported as described in [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

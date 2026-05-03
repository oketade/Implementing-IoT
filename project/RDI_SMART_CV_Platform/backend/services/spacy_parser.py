import re
import spacy

_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", re.I)
_PHONE = re.compile(r"(\+?\d[\d\s\-().]{6,}\d)")
_DATE_RANGE = re.compile(
    r"\b(\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z\s,]*"
    r"[\d]*\s*[–\-—]\s*(\d{4}|present|current|now|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z\s\d]*",
    re.I
)
_DEGREE = re.compile(
    r"(bachelor[^\n,]*|master[^\n,]*|phd[^\n,]*|doctorate[^\n,]*|"
    r"diploma[^\n,]*|b\.?sc[^\n,]*|m\.?sc[^\n,]*|b\.?eng[^\n,]*|"
    r"m\.?eng[^\n,]*|mba[^\n,]*|associate[^\n,]*|"
    r"[a-z ]*(?:information technology|computer science|software engineering|"
    r"business administration|data science)[^\n,]*)",
    re.I
)

_SKILLS_POOL = {
    "python","javascript","typescript","java","c++","c#","go","rust","ruby","php","swift","kotlin",
    "react","vue","angular","svelte","nextjs","node","nodejs","express",
    "django","flask","fastapi","spring","laravel",
    "sql","postgresql","mysql","sqlite","mongodb","redis","elasticsearch",
    "docker","kubernetes","aws","azure","gcp","terraform","ansible","linux","bash",
    "git","rest","graphql","grpc","mqtt","iot","embedded c","embedded systems",
    "html","css","sass","figma","sketch","tailwind",
    "machine learning","deep learning","pytorch","tensorflow","scikit-learn",
    "pandas","numpy","data analysis","power bi","tableau",
    "agile","scrum","jira","ci/cd","devops",
}

_SEC = {
    "experience": re.compile(
        r"^\s*(work\s+experience|experience|employment|career|"
        r"professional\s+experience|project\s+experience|"
        r"internships?|work\s+history|employment\s+history|"
        r"career\s+history|relevant\s+experience)\s*$",
        re.I
    ),

    "education": re.compile(
        r"^\s*(education|academic|qualification|studies|"
        r"academic\s+background|educational\s+background)\s*$",
        re.I
    ),

    "skills": re.compile(
        r"^\s*(skills|technical\s+skills|technologies|tools|"
        r"competencies|expertise|tech\s+stack)\s*$",
        re.I
    ),

    "summary": re.compile(
        r"^\s*(summary|profile|objective|about|introduction|"
        r"professional\s+summary|career\s+summary)\s*$",
        re.I
    ),
}


def parse(raw_text: str) -> dict:
    nlp  = _get_nlp()
    # Keep empty lines for block splitting — only strip, don't filter
    all_lines  = [l.rstrip() for l in raw_text.splitlines()]
    clean_lines = [l for l in all_lines if l.strip()]
    doc = nlp(raw_text[:5000])  # spaCy has a token limit; first 5000 chars is enough for NER

    return {
        "name":       _extract_name(doc, clean_lines),
        "email":      _extract_email(raw_text),
        "phone":      _extract_phone(raw_text),
        "location":   _extract_location(doc),
        "summary":    _extract_summary(all_lines),
        "skills":     _extract_skills(raw_text),
        "experience": _extract_experience(all_lines),
        "education":  _extract_education(all_lines),
    }


def _extract_name(doc, lines: list) -> str:
    top_doc = _get_nlp()(" ".join(lines[:5]))
    for ent in top_doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            return ent.text.strip()
    for line in lines[:4]:
        if "@" not in line and re.match(r"^[A-Z][a-z]+([ \-][A-Z][a-z]+){1,3}$", line.strip()):
            return line.strip()
    return ""


def _extract_email(text: str) -> str:
    m = _EMAIL.search(text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    for m in _PHONE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 7 <= len(digits) <= 15:
            return m.group(0).strip()
    return ""


def _extract_location(doc) -> str:
    for ent in doc.ents:
        if ent.label_ in ("GPE", "LOC"):
            return ent.text.strip()
    return ""


def _extract_skills(text: str) -> list:
    lower = text.lower()
    found = []
    for skill in sorted(_SKILLS_POOL):
        if re.search(r"\b" + re.escape(skill) + r"\b", lower):
            found.append(skill.title() if " " not in skill else skill.title())
    return found


def _extract_summary(all_lines: list) -> str:
    for i, line in enumerate(all_lines):
        if _SEC["summary"].match(line):
            chunk = []
            for l in all_lines[i + 1: i + 10]:
                if any(p.match(l) for p in _SEC.values()):
                    break
                if l.strip():
                    chunk.append(l.strip())
                elif chunk:
                    break
            text = " ".join(chunk).strip()
            if len(text) > 30:
                return text
    # Fallback: longest non-heading line
    candidates = [
        l.strip() for l in all_lines
        if len(l.strip()) > 60
        and "@" not in l
        and not any(p.match(l) for p in _SEC.values())
    ]
    return candidates[0] if candidates else ""


def _extract_experience(all_lines: list) -> list:
    blocks = _get_section_blocks(all_lines, "experience")
    results = []
    for block in blocks:
        if not any(l.strip() for l in block):
            continue
        e = _parse_exp_block([l for l in block if l.strip()])
        if e["title"] or e["company"]:
            results.append(e)
    return results


def _parse_exp_block(lines: list) -> dict:
    title, company, period, desc_lines = "", "", "", []

    for line in lines:
        # Date range
        dm = _DATE_RANGE.search(line)
        if dm and not period:
            period = dm.group(0).strip()
            continue

        # spaCy ORG
        ldoc = _get_nlp()(line)
        orgs = [e.text for e in ldoc.ents if e.label_ == "ORG"]

        words = line.split()
        is_short = len(words) <= 6
        is_titlecase = sum(1 for w in words if w and w[0].isupper()) >= max(1, len(words) // 2)

        if not title and is_short and is_titlecase and "@" not in line:
            title = line.strip()
        elif not company and orgs:
            company = orgs[0]
        elif not company and is_short and is_titlecase and line != title:
            company = line.strip()
        else:
            desc_lines.append(line)

    return {
        "title":       title,
        "company":     company,
        "period":      period,
        "description": " ".join(desc_lines).strip(),
        "type":        "Full-time",
    }


def _extract_education(all_lines: list) -> list:
    blocks = _get_section_blocks(all_lines, "education")
    results = []
    for block in blocks:
        clean = [l for l in block if l.strip()]
        if not clean:
            continue

        degree, institution, period, status = "", "", "", "Completed"

        for line in clean:
            dm = _DATE_RANGE.search(line)
            if dm and not period:
                period = dm.group(0).strip()
                if re.search(r"present|current|ongoing", period, re.I):
                    status = "Current"
                continue

            deg_m = _DEGREE.search(line)
            if deg_m and not degree:
                degree = deg_m.group(0).strip()
                continue

            ldoc = _get_nlp()(line)
            orgs = [e.text for e in ldoc.ents if e.label_ == "ORG"]
            if orgs and not institution:
                institution = orgs[0]
                continue

            # Fallback: line with "university", "college", "institute"
            if re.search(r"(university|college|institute|school|academy)", line, re.I) and not institution:
                institution = line.strip()
                continue

            if not degree and len(line.split()) >= 3:
                degree = line.strip()

        if degree or institution:
            results.append({"degree": degree, "institution": institution,
                            "period": period, "status": status})
    return results


def normalize_heading(line: str) -> str:
    return re.sub(r"\s+", "", line).lower()


def _get_section_blocks(all_lines: list, section: str) -> list:
    heading_pat = _SEC[section]
    other_pats  = [v for k, v in _SEC.items() if k != section]

    in_section    = False
    current_block: list = []
    blocks:        list = []

    for line in all_lines:
        normalized = normalize_heading(line)

        if not in_section:
            if heading_pat.match(line) or heading_pat.match(normalized):
                in_section = True
            continue

        if line.strip() and any(
            p.match(line) or p.match(normalized) for p in other_pats
        ):
            break

        if not line.strip():
            if current_block:
                blocks.append(current_block)
                current_block = []
        else:
            current_block.append(line.strip())

    if current_block:
        blocks.append(current_block)

    return blocks






# import re
# import spacy


# # Load spaCy model 

# _nlp = None

# def _get_nlp():
#     global _nlp
#     if _nlp is None:
#         _nlp = spacy.load("en_core_web_sm")
#     return _nlp



# # BASIC REGEX PATTERNS


# # Email detection
# _EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", re.I)

# # Phone number detection
# _PHONE = re.compile(r"(\+?\d[\d\s\-().]{6,}\d)")

# # Date range (e.g., 2023 – 2025)
# _DATE_RANGE = re.compile(
#     r"\b(\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z\s,]*"
#     r"[\d]*\s*[–\-—]\s*(\d{4}|present|current|now)[a-z\s\d]*",
#     re.I
# )

# # Degree detection
# _DEGREE = re.compile(
#     r"(bachelor[^\n,]*|master[^\n,]*|phd[^\n,]*|"
#     r"[a-z ]*(?:information technology|computer science|software engineering)[^\n,]*)",
#     re.I
# )



# # SKILLS DATABASE 

# _SKILLS_POOL = {
#     "python","javascript","typescript","java","c++","c#","go","rust","ruby","php","swift","kotlin",
#     "react","vue","angular","svelte","nextjs","node","nodejs","express",
#     "django","flask","fastapi","spring","laravel",
#     "sql","postgresql","mysql","sqlite","mongodb","redis","elasticsearch",
#     "docker","kubernetes","aws","azure","gcp","terraform","ansible","linux","bash",
#     "git","rest","graphql","grpc","mqtt","iot","embedded c","embedded systems",
#     "html","css","sass","figma","sketch","tailwind",
#     "machine learning","deep learning","pytorch","tensorflow","scikit-learn",
#     "pandas","numpy","data analysis","power bi","tableau",
#     "agile","scrum","jira","ci/cd","devops",
# }



# # SECTION DETECTION (VERY IMPORTANT)

# _SEC = {
#     "experience": re.compile(
#         r"^\s*(work\s+experience|experience|employment|career|"
#         r"professional\s+experience|project\s+experience|"
#         r"internships?|work\s+history|employment\s+history)\s*$",
#         re.I
#     ),
#     "education": re.compile(r"(education|academic)", re.I),
#     "skills": re.compile(r"(skills|technologies|tools)", re.I),
#     "summary": re.compile(r"(summary|profile|about)", re.I),
# }



# # NORMALIZE TEXT
# # Handles weird headings like "P R O F I L E"

# def normalize_heading(line: str) -> str:
#     return re.sub(r"\s+", "", line).lower()



# # MAIN PARSER FUNCTION

# def parse(raw_text: str) -> dict:
#     """
#     This is the main function.
#     It takes raw CV text and returns structured data.
#     """

#     nlp = _get_nlp()

#     # Split CV into lines
#     all_lines = [l.rstrip() for l in raw_text.splitlines()]
#     clean_lines = [l for l in all_lines if l.strip()]

#     # Run spaCy (for names, locations, etc.)
#     doc = nlp(raw_text[:5000])

#     return {
#         "name": _extract_name(doc, clean_lines),
#         "email": _extract_email(raw_text),
#         "phone": _extract_phone(raw_text),
#         "location": _extract_location(doc),
#         "summary": _extract_summary(all_lines),
#         "skills": _extract_skills(raw_text),
#         "experience": _extract_experience(all_lines),
#         "education": _extract_education(all_lines),
#     }



# # BASIC INFO EXTRACTION

# def _extract_name(doc, lines):
#     for ent in doc.ents:
#         if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
#             return ent.text.strip()
#     return ""

# def _extract_email(text):
#     m = _EMAIL.search(text)
#     return m.group(0) if m else ""

# def _extract_phone(text):
#     m = _PHONE.search(text)
#     return m.group(0) if m else ""

# def _extract_location(doc):
#     for ent in doc.ents:
#         if ent.label_ in ("GPE", "LOC"):
#             return ent.text
#     return ""



# # SKILLS EXTRACTION (ACCURATE MATCHING)

# def _extract_skills(text):
#     lower = text.lower()
#     found = set()

#     for skill in _SKILLS_POOL:
#         pattern = r"\b" + re.escape(skill.lower()) + r"\b"

#         if re.search(pattern, lower):
#             found.add(skill.title())

#     return sorted(found)



# # SUMMARY EXTRACTION

# def _extract_summary(lines):
#     """
#     Finds the summary/profile section
#     """

#     for i, line in enumerate(lines):
#         normalized = normalize_heading(line)

#         # detect summary heading
#         if _SEC["summary"].search(line) or _SEC["summary"].search(normalized):

#             summary = []

#             for l in lines[i+1:i+10]:
#                 norm_l = normalize_heading(l)

#                 # stop when another section starts
#                 if any(_SEC[k].search(l) or _SEC[k].search(norm_l) for k in _SEC):
#                     break

#                 if l.strip():
#                     summary.append(l.strip())

#             return " ".join(summary)

#     return ""



# # EXPERIENCE EXTRACTION (PROJECT + JOB SUPPORT)

# def _extract_experience(lines):
#     blocks = _get_section_blocks(lines, "experience")
#     results = []

#     for block in blocks:
#         exp = _parse_exp_block(block)
#         if exp["title"]:
#             results.append(exp)

#     return results


# def _parse_exp_block(lines):
#     """
#     Handles both:
#     - Job experience
#     - Project experience (your case)
#     """

#     title, company, period = "", "", ""
#     desc_lines = []

#     for line in lines:

#         # detect project title (important fix)
#         if not title:
#             if "(" in line and ")" in line:
#                 title = line.strip()
#                 continue

#             if len(line.split()) >= 3 and not line.startswith("–"):
#                 title = line.strip()
#                 continue

#         # detect dates
#         dm = _DATE_RANGE.search(line)
#         if dm and not period:
#             period = dm.group(0)
#             continue

#         # detect company using spaCy
#         if not company:
#             ldoc = _get_nlp()(line)
#             orgs = [e.text for e in ldoc.ents if e.label_ == "ORG"]
#             if orgs:
#                 company = orgs[0]
#                 continue

#         # everything else is description
#         desc_lines.append(line)

#     return {
#         "title": title,
#         "company": company,
#         "period": period,
#         "description": " ".join(desc_lines),
#         "type": "Project" if company == "" else "Work",
#     }



# # EDUCATION EXTRACTION

# def _extract_education(lines):
#     blocks = _get_section_blocks(lines, "education")
#     results = []

#     for block in blocks:
#         text = " ".join(block)
#         degree = _DEGREE.search(text)

#         results.append({
#             "degree": degree.group(0) if degree else "",
#             "institution": "",
#         })

#     return results



# # SECTION SPLITTER 

# def _get_section_blocks(lines, section):
#     """
#     This function finds where a section starts
#     and groups its content properly.
#     """

#     section_pattern = _SEC[section]
#     other_sections = [v for k, v in _SEC.items() if k != section]

#     in_section = False
#     blocks = []
#     current = []

#     for line in lines:
#         norm = normalize_heading(line)

#         # detect section start
#         if not in_section:
#             if section_pattern.search(line) or section_pattern.search(norm):
#                 in_section = True
#             continue

#         # stop if another section appears
#         if any(p.search(line) or p.search(norm) for p in other_sections):
#             break

#         # split blocks
#         if not line.strip():
#             if current:
#                 blocks.append(current)
#                 current = []
#         else:
#             current.append(line.strip())

#     if current:
#         blocks.append(current)

#     return blocks





# import re
# import spacy


# # ============================================
# # Load spaCy model (only once for performance)
# # ============================================
# _nlp = None

# def _get_nlp():
#     global _nlp
#     if _nlp is None:
#         _nlp = spacy.load("en_core_web_sm")
#     return _nlp


# # ============================================
# # BASIC REGEX PATTERNS
# # ============================================

# # Email detection
# _EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", re.I)

# # Phone number detection
# _PHONE = re.compile(r"(\+?\d[\d\s\-().]{6,}\d)")

# # Date range detection (e.g., 2022 – 2024)
# _DATE_RANGE = re.compile(
#     r"\b(\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z\s,]*"
#     r"[\d]*\s*[–\-—]\s*(\d{4}|present|current|now)[a-z\s\d]*",
#     re.I
# )

# # Degree detection
# _DEGREE = re.compile(
#     r"(bachelor[^\n,]*|master[^\n,]*|phd[^\n,]*|"
#     r"[a-z ]*(?:information technology|computer science|software engineering)[^\n,]*)",
#     re.I)


# # ============================================
# # SKILLS DATABASE (BIG = MORE ACCURATE)
# # ============================================
# _SKILLS_POOL = {
#     "python","javascript","typescript","java","c++","c#","go","rust","ruby","php","swift","kotlin",
#     "react","vue","angular","svelte","nextjs","node","nodejs","express",
#     "django","flask","fastapi","spring","laravel",
#     "sql","postgresql","mysql","sqlite","mongodb","redis","elasticsearch",
#     "docker","kubernetes","aws","azure","gcp","terraform","ansible","linux","bash",
#     "git","rest","graphql","grpc","mqtt","iot","embedded c","embedded systems",
#     "html","css","sass","figma","sketch","tailwind",
#     "machine learning","deep learning","pytorch","tensorflow","scikit-learn",
#     "pandas","numpy","data analysis","power bi","tableau",
#     "agile","scrum","jira","ci/cd","devops",
# }


# # ============================================
# # SECTION DETECTION
# # (Handles different CV formats)
# # ============================================
# _SEC = {
#     "experience": re.compile(
#         r"(work\s+experience|experience|employment|career|"
#         r"professional\s+experience|project\s+experience|"
#         r"internships?|work\s+history|employment\s+history|"
#         r"relevant\s+experience|projects?|relevant\s+projects|"
#         r"internship\s+experience)",
#         re.I
#     ),
#     "education": re.compile(r"(education|academic)", re.I),
#     "skills": re.compile(r"(skills|technologies|tools)", re.I),
#     "summary": re.compile(r"(summary|profile|about)", re.I),
# }


# # ============================================
# # Normalize text
# # Handles things like "P R O F I L E"
# # ============================================
# def normalize_heading(line: str) -> str:
#     return re.sub(r"\s+", "", line).lower()


# # ============================================
# # MAIN PARSER FUNCTION
# # ============================================
# def parse(raw_text: str) -> dict:
#     """
#     Main function that extracts structured data from CV text
#     """

#     nlp = _get_nlp()

#     # Split text into lines
#     lines = [l.rstrip() for l in raw_text.splitlines()]

#     # Use spaCy for entity detection
#     doc = nlp(raw_text[:5000])

#     return {
#         "name": _extract_name(doc),
#         "email": _extract_email(raw_text),
#         "phone": _extract_phone(raw_text),
#         "location": _extract_location(doc),
#         "summary": _extract_summary(lines),
#         "skills": _extract_skills(raw_text),
#         "experience": _extract_experience(lines),
#         "education": _extract_education(lines),
#     }


# # ============================================
# # BASIC INFO EXTRACTION
# # ============================================
# def _extract_name(doc):
#     for ent in doc.ents:
#         if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
#             return ent.text.strip()
#     return ""


# def _extract_email(text):
#     m = _EMAIL.search(text)
#     return m.group(0) if m else ""


# def _extract_phone(text):
#     m = _PHONE.search(text)
#     return m.group(0) if m else ""


# def _extract_location(doc):
#     for ent in doc.ents:
#         if ent.label_ in ("GPE", "LOC"):
#             return ent.text
#     return ""


# # ============================================
# # SKILLS EXTRACTION (precise matching)
# # ============================================
# def _extract_skills(text):
#     lower = text.lower()
#     found = set()

#     for skill in _SKILLS_POOL:
#         if re.search(r"\b" + re.escape(skill) + r"\b", lower):
#             found.add(skill.title())

#     return sorted(found)


# # ============================================
# # SUMMARY EXTRACTION
# # ============================================
# def _extract_summary(lines):
#     for i, line in enumerate(lines):
#         norm = normalize_heading(line)

#         if _SEC["summary"].search(line) or _SEC["summary"].search(norm):
#             summary = []

#             for l in lines[i+1:i+10]:
#                 norm_l = normalize_heading(l)

#                 if any(_SEC[k].search(l) or _SEC[k].search(norm_l) for k in _SEC):
#                     break

#                 if l.strip():
#                     summary.append(l.strip())

#             return " ".join(summary)

#     return ""


# # ============================================
# # EXPERIENCE EXTRACTION
# # ============================================
# def _extract_experience(lines):
#     blocks = _get_section_blocks(lines, "experience")
#     results = []

#     for block in blocks:
#         exp = _parse_exp_block(block)
#         if exp["title"]:
#             results.append(exp)

#     return results


# def _parse_exp_block(lines):
#     title, company, period = "", "", ""
#     desc = []

#     for line in lines:

#         # detect titles with dash (important for real CVs)
#         if not title and "–" in line:
#             title = line.strip()
#             continue

#         # detect titles with brackets
#         if not title and "(" in line and ")" in line:
#             title = line.strip()
#             continue

#         # fallback title detection
#         if not title and len(line.split()) >= 3 and not line.startswith("–"):
#             title = line.strip()
#             continue

#         # detect dates
#         dm = _DATE_RANGE.search(line)
#         if dm and not period:
#             period = dm.group(0)
#             continue

#         # detect company
#         if not company:
#             ldoc = _get_nlp()(line)
#             orgs = [e.text for e in ldoc.ents if e.label_ == "ORG"]
#             if orgs:
#                 company = orgs[0]
#                 continue

#         desc.append(line)

#     return {
#         "title": title,
#         "company": company,
#         "period": period,
#         "description": " ".join(desc),
#         "type": "Project" if not company else "Work",
#     }


# # ============================================
# # EDUCATION EXTRACTION
# # ============================================
# def _extract_education(lines):
#     blocks = _get_section_blocks(lines, "education")
#     results = []

#     for block in blocks:
#         text = " ".join(block)
#         degree = _DEGREE.search(text)

#         results.append({
#             "degree": degree.group(0) if degree else "",
#             "institution": "",
#         })

#     return results


# # ============================================
# # SECTION SPLITTING (VERY IMPORTANT)
# # ============================================
# def _get_section_blocks(lines, section):
#     section_pattern = _SEC[section]
#     other_sections = [v for k, v in _SEC.items() if k != section]

#     in_section = False
#     blocks = []
#     current = []

#     for line in lines:
#         norm = normalize_heading(line)

#         # start section
#         if not in_section:
#             if section_pattern.search(line) or section_pattern.search(norm):
#                 in_section = True
#             continue

#         # detect new section → close current block but continue scanning
#         if any(p.search(line) or p.search(norm) for p in other_sections):
#             if current:
#                 blocks.append(current)
#                 current = []
#             in_section = False
#             continue

#         # split blocks by empty line
#         if not line.strip():
#             if current:
#                 blocks.append(current)
#                 current = []
#         else:
#             current.append(line.strip())

#     if current:
#         blocks.append(current)

#     return blocks





# import re
# import spacy

# _nlp = None


# def _get_nlp():
#     global _nlp
#     if _nlp is None:
#         _nlp = spacy.load("en_core_web_sm")
#     return _nlp


# # ---------------------------------------------------------------------------
# # Regex patterns
# # ---------------------------------------------------------------------------

# _EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", re.I)

# _PHONE = re.compile(r"(\+?\d[\d\s\-().]{6,}\d)")

# _DATE_RANGE = re.compile(
#     r"\b(\d{4}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z\s,]*"
#     r"[\d]*\s*[–\-—~]\s*"
#     r"(\d{4}|present|current|now|ongoing|jan|feb|mar|apr|may|jun|jul|"
#     r"aug|sep|oct|nov|dec)[a-z\s\d]*",
#     re.I,
# )

# _DEGREE = re.compile(
#     r"(bachelor[^\n,]*|master[^\n,]*|phd[^\n,]*|doctorate[^\n,]*|"
#     r"diploma[^\n,]*|b\.?sc[^\n,]*|m\.?sc[^\n,]*|b\.?eng[^\n,]*|"
#     r"m\.?eng[^\n,]*|b\.?a\b[^\n,]*|m\.?a\b[^\n,]*|mba[^\n,]*|"
#     r"associate[^\n,]*)",
#     re.I,
# )

# _INSTITUTION_KEYWORDS = re.compile(
#     r"(university|college|institute|polytechnic|academy|school of|"
#     r"universit[äà]t|école|universidad|高校|学院)",
#     re.I,
# )

# _BULLET_PREFIX = re.compile(r"^[\s\-–—•·*▪→>]+")

# # Project title pattern: "Project Name (Tag, Tag)"
# _PROJECT_TITLE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")


# # ---------------------------------------------------------------------------
# # Skill detection
# # ---------------------------------------------------------------------------

# _SKILLS_POOL = {
#     # Languages
#     "python", "javascript", "typescript", "java", "c++", "c#", "go",
#     "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
#     # Frontend
#     "react", "vue", "angular", "svelte", "nextjs", "node", "nodejs",
#     "express", "html", "css", "sass", "tailwind", "chart.js",
#     # Backend
#     "django", "flask", "fastapi", "spring", "laravel", "websocket",
#     # Databases
#     "sql", "postgresql", "mysql", "sqlite", "mongodb", "redis",
#     "elasticsearch", "json storage",
#     # DevOps
#     "docker", "kubernetes", "aws", "azure", "gcp", "terraform",
#     "ansible", "linux", "bash", "swagger",
#     # APIs / protocols
#     "git", "rest", "graphql", "grpc", "mqtt", "rest apis",
#     # IoT / embedded
#     "iot", "embedded c", "embedded systems", "raspberry pi",
#     "raspberry pi pico w", "micropython", "arduino", "pwm",
#     "home assistant",
#     # Design
#     "figma", "sketch",
#     # ML / data
#     "machine learning", "deep learning", "pytorch", "tensorflow",
#     "scikit-learn", "pandas", "numpy", "data analysis",
#     "power bi", "tableau",
#     # Methods
#     "agile", "scrum", "jira", "ci/cd", "devops",
#     # Security
#     "bcrypt",
# }

# _SKILL_DISPLAY = {
#     "iot": "IoT",
#     "javascript": "JavaScript",
#     "typescript": "TypeScript",
#     "nodejs": "Node.js",
#     "node": "Node.js",
#     "fastapi": "FastAPI",
#     "postgresql": "PostgreSQL",
#     "sqlite": "SQLite",
#     "mongodb": "MongoDB",
#     "mysql": "MySQL",
#     "mqtt": "MQTT",
#     "ci/cd": "CI/CD",
#     "rest": "REST",
#     "rest apis": "REST APIs",
#     "graphql": "GraphQL",
#     "grpc": "gRPC",
#     "html": "HTML",
#     "css": "CSS",
#     "sql": "SQL",
#     "aws": "AWS",
#     "gcp": "GCP",
#     "nextjs": "Next.js",
#     "raspberry pi pico w": "Raspberry Pi Pico W",
#     "micropython": "MicroPython",
#     "pwm": "PWM",
#     "json storage": "JSON Storage",
#     "chart.js": "Chart.js",
#     "c++": "C++",
#     "c#": "C#",
#     "power bi": "Power BI",
# }


# # ---------------------------------------------------------------------------
# # Section heading patterns
# # ---------------------------------------------------------------------------

# _SEC = {
#     "experience": re.compile(
#         r"^\s*(work\s+experience|experience|employment|career|"
#         r"professional\s+experience|"
#         r"internships?|work\s+history|employment\s+history|"
#         r"career\s+history|relevant\s+experience)\s*$",
#         re.I,
#     ),
#     "projects": re.compile(
#         r"^\s*(projects?|project\s+experience|"
#         r"personal\s+projects|side\s+projects|portfolio|"
#         r"selected\s+projects)\s*$",
#         re.I,
#     ),
#     "education": re.compile(
#         r"^\s*(education|academic|qualifications?|studies|"
#         r"academic\s+background|educational\s+background|"
#         r"academic\s+qualifications)\s*$",
#         re.I,
#     ),
#     "skills": re.compile(
#         r"^\s*(skills|technical\s+skills|technologies|tools|"
#         r"competencies|expertise|tech\s+stack)\s*$",
#         re.I,
#     ),
#     "summary": re.compile(
#         r"^\s*(summary|profile|objective|about|introduction|"
#         r"professional\s+summary|career\s+summary)\s*$",
#         re.I,
#     ),
# }


# # ---------------------------------------------------------------------------
# # Helpers
# # ---------------------------------------------------------------------------

# def _strip_bullet(line: str) -> str:
#     """Remove leading bullet markers like -, –, •, *, etc."""
#     return _BULLET_PREFIX.sub("", line).strip()


# def _normalize_heading(line: str) -> str:
#     return re.sub(r"\s+", "", line).lower()


# def _is_section_heading(line: str) -> bool:
#     """True if the line matches any known section heading."""
#     stripped = line.strip()
#     if not stripped:
#         return False
#     normalized = _normalize_heading(stripped)
#     return any(
#         p.match(stripped) or p.match(normalized) for p in _SEC.values()
#     )


# def _get_section_blocks(all_lines: list, section: str) -> list:
#     """
#     Return the lines under a given section heading, split into blocks
#     by blank lines. Stops when another section heading is reached.
#     """
#     if section not in _SEC:
#         return []

#     heading_pat = _SEC[section]
#     other_pats = [v for k, v in _SEC.items() if k != section]

#     in_section = False
#     current_block: list = []
#     blocks: list = []

#     for line in all_lines:
#         normalized = _normalize_heading(line)

#         if not in_section:
#             if heading_pat.match(line) or heading_pat.match(normalized):
#                 in_section = True
#             continue

#         if line.strip() and any(
#             p.match(line) or p.match(normalized) for p in other_pats
#         ):
#             break

#         if not line.strip():
#             if current_block:
#                 blocks.append(current_block)
#                 current_block = []
#         else:
#             current_block.append(line.strip())

#     if current_block:
#         blocks.append(current_block)

#     return blocks


# # ---------------------------------------------------------------------------
# # Main parse function
# # ---------------------------------------------------------------------------

# def parse(raw_text: str) -> dict:
#     nlp = _get_nlp()
#     all_lines = [l.rstrip() for l in raw_text.splitlines()]
#     clean_lines = [l for l in all_lines if l.strip()]
#     doc = nlp(raw_text[:5000])

#     name = _extract_name(doc, clean_lines)
#     email = _extract_email(raw_text)
#     phone = _extract_phone(raw_text)
#     location = _extract_location(doc)
#     summary = _extract_summary(all_lines)
#     skills = _extract_skills(raw_text)
#     experience = _extract_experience(all_lines)
#     projects = _extract_projects(all_lines)
#     education = _extract_education(all_lines)

#     result = {
#         "name": name,
#         "email": email,
#         "phone": phone,
#         "location": location,
#         "summary": summary,
#         "skills": skills,
#         "experience": experience,
#         "projects": projects,
#         "education": education,
#     }

#     # Add confidence scores per field — frontend can use these to
#     # decide whether to show "auto-filled" badge or leave blank.
#     result["confidence"] = _score_confidence(result)
#     return result


# # ---------------------------------------------------------------------------
# # Field extractors
# # ---------------------------------------------------------------------------

# def _extract_name(doc, lines: list) -> str:
#     top_doc = _get_nlp()(" ".join(lines[:5]))
#     for ent in top_doc.ents:
#         if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
#             return ent.text.strip()
#     for line in lines[:4]:
#         stripped = line.strip()
#         if "@" in stripped:
#             continue
#         if re.match(r"^[A-Z][a-z]+([ \-][A-Z][a-z]+){1,3}$", stripped):
#             return stripped
#     return ""


# def _extract_email(text: str) -> str:
#     m = _EMAIL.search(text)
#     return m.group(0) if m else ""


# def _extract_phone(text: str) -> str:
#     for m in _PHONE.finditer(text):
#         digits = re.sub(r"\D", "", m.group(0))
#         if 7 <= len(digits) <= 15:
#             return m.group(0).strip()
#     return ""


# def _extract_location(doc) -> str:
#     for ent in doc.ents:
#         if ent.label_ in ("GPE", "LOC"):
#             return ent.text.strip()
#     return ""


# def _extract_skills(text: str) -> list:
#     lower = text.lower()
#     found = []
#     seen = set()
#     # Sort by length desc so multi-word skills match before single words
#     # (prevents "rest" from being added when "rest apis" is present)
#     for skill in sorted(_SKILLS_POOL, key=len, reverse=True):
#         if re.search(r"\b" + re.escape(skill) + r"\b", lower):
#             display = _SKILL_DISPLAY.get(skill, skill.title())
#             if display.lower() not in seen:
#                 found.append(display)
#                 seen.add(display.lower())
#     return sorted(found)


# def _extract_summary(all_lines: list) -> str:
#     # Pass 1: find the explicit Summary/Profile section
#     for i, line in enumerate(all_lines):
#         if _SEC["summary"].match(line.strip()):
#             chunk = []
#             for l in all_lines[i + 1: i + 12]:
#                 if _is_section_heading(l):
#                     break
#                 if l.strip():
#                     chunk.append(l.strip())
#                 elif chunk:
#                     break
#             text = " ".join(chunk).strip()
#             if 30 < len(text) < 1000:
#                 return text

#     # Pass 2: stricter fallback — must look like prose, not a label list
#     for l in all_lines:
#         s = l.strip()
#         if len(s) < 80 or len(s) > 600:
#             continue
#         if "@" in s or "http" in s:
#             continue
#         if _is_section_heading(s):
#             continue
#         # Reject comma-heavy lines (skill lists)
#         word_count = len(s.split())
#         if word_count == 0:
#             continue
#         if s.count(",") / word_count > 0.15:
#             continue
#         # Require sentence-ish punctuation
#         if not re.search(r"[.!?]", s):
#             continue
#         return s

#     return ""


# # ---------------------------------------------------------------------------
# # Experience (real jobs)
# # ---------------------------------------------------------------------------

# def _extract_experience(all_lines: list) -> list:
#     blocks = _get_section_blocks(all_lines, "experience")
#     results = []
#     for block in blocks:
#         clean = [_strip_bullet(l) for l in block if l.strip()]
#         if not clean:
#             continue
#         e = _parse_exp_block(clean)
#         if e["title"] or e["company"]:
#             results.append(e)
#     return results


# def _parse_exp_block(lines: list) -> dict:
#     """
#     Heuristic: in a job entry, the first two non-bullet, non-date
#     lines are usually title and company in some order. Bullet lines
#     are description. Date is anywhere.
#     """
#     title, company, period = "", "", ""
#     desc_lines = []
#     header_candidates = []

#     for raw_line in lines:
#         line = raw_line.strip()

#         # Date range — assign to period
#         dm = _DATE_RANGE.search(line)
#         if dm and not period:
#             period = dm.group(0).strip()
#             # If the line is ONLY a date, skip; otherwise also process
#             if re.sub(r"\s+", "", line) == re.sub(r"\s+", "", dm.group(0)):
#                 continue

#         # Original line had a bullet prefix? Treat as description
#         if _BULLET_PREFIX.match(raw_line) or raw_line != line:
#             # Note: at this point `lines` already had bullets stripped,
#             # so this branch rarely fires. Keep length-based fallback below.
#             desc_lines.append(line)
#             continue

#         words = line.split()
#         is_short = len(words) <= 8
#         is_titlecase = (
#             sum(1 for w in words if w and w[0].isupper())
#             >= max(1, len(words) // 2)
#         )

#         if is_short and is_titlecase:
#             header_candidates.append(line)
#         else:
#             desc_lines.append(line)

#     # Assign first two header candidates to title and company
#     if len(header_candidates) >= 1:
#         title = header_candidates[0]
#     if len(header_candidates) >= 2:
#         company = header_candidates[1]

#     return {
#         "title": title,
#         "company": company,
#         "period": period,
#         "description": " ".join(desc_lines).strip(),
#         "type": "Full-time",
#     }


# # ---------------------------------------------------------------------------
# # Projects (separate from work experience)
# # ---------------------------------------------------------------------------

# def _extract_projects(all_lines: list) -> list:
#     blocks = _get_section_blocks(all_lines, "projects")
#     results = []
#     for block in blocks:
#         clean = [l for l in block if l.strip()]
#         if not clean:
#             continue

#         # First line: project name, possibly with "(tags)"
#         title_line = clean[0].strip()
#         m = _PROJECT_TITLE.match(title_line)
#         if m:
#             name = m.group(1).strip()
#             tags = [t.strip() for t in m.group(2).split(",")]
#         else:
#             name = title_line
#             tags = []

#         bullets = []
#         for line in clean[1:]:
#             cleaned = _strip_bullet(line)
#             if cleaned:
#                 bullets.append(cleaned)

#         if name and len(name) < 200:
#             results.append({
#                 "name": name,
#                 "tags": tags,
#                 "bullets": bullets,
#                 "description": " ".join(bullets),
#             })
#     return results


# # ---------------------------------------------------------------------------
# # Education
# # ---------------------------------------------------------------------------

# def _extract_education(all_lines: list) -> list:
#     blocks = _get_section_blocks(all_lines, "education")
#     results = []
#     for block in blocks:
#         clean = [_strip_bullet(l) for l in block if l.strip()]
#         if not clean:
#             continue

#         degree = ""
#         institution = ""
#         period = ""
#         status = "Completed"
#         used = set()

#         # Pass 1: high-confidence patterns
#         for i, line in enumerate(clean):
#             # Date range
#             dm = _DATE_RANGE.search(line)
#             if dm and not period:
#                 period = dm.group(0).strip()
#                 if re.search(
#                     r"present|current|ongoing", period, re.I
#                 ):
#                     status = "Current"
#                 used.add(i)
#                 continue

#             # Institution by keyword
#             if not institution and _INSTITUTION_KEYWORDS.search(line):
#                 institution = line.strip()
#                 used.add(i)
#                 continue

#             # Degree by keyword
#             if not degree:
#                 deg_m = _DEGREE.search(line)
#                 if deg_m:
#                     degree = deg_m.group(0).strip()
#                     used.add(i)
#                     continue

#         # Pass 2: fill gaps with reasonable fallbacks
#         for i, line in enumerate(clean):
#             if i in used:
#                 continue
#             if not degree and 2 <= len(line.split()) <= 12:
#                 degree = line.strip()
#                 used.add(i)
#                 continue
#             if (
#                 not institution
#                 and 2 <= len(line.split()) <= 12
#                 and not _DATE_RANGE.search(line)
#             ):
#                 institution = line.strip()
#                 used.add(i)

#         if degree or institution:
#             results.append({
#                 "degree": degree,
#                 "institution": institution,
#                 "period": period,
#                 "status": status,
#             })
#     return results


# # ---------------------------------------------------------------------------
# # Confidence scoring — frontend can use this to decide whether to
# # show the "auto-filled" badge or leave the field empty for manual entry.
# # ---------------------------------------------------------------------------

# def _score_confidence(result: dict) -> dict:
#     """
#     Return a dict of field_name -> confidence score (0.0 to 1.0).
#     Use 0.6+ as the threshold for showing as auto-filled.
#     """
#     scores = {}

#     scores["name"] = 0.9 if result["name"] else 0.0
#     scores["email"] = 1.0 if result["email"] else 0.0
#     scores["phone"] = 0.9 if result["phone"] else 0.0
#     scores["location"] = 0.7 if result["location"] else 0.0

#     # Summary: high if found via section, low if fallback
#     if result["summary"]:
#         s = result["summary"]
#         # Penalize if it looks like a label list
#         if s.count(",") / max(1, len(s.split())) > 0.1:
#             scores["summary"] = 0.3
#         else:
#             scores["summary"] = 0.85
#     else:
#         scores["summary"] = 0.0

#     scores["skills"] = min(1.0, len(result["skills"]) / 5)

#     # Experience: high only if every entry has both title and company
#     if result["experience"]:
#         complete = sum(
#             1 for e in result["experience"]
#             if e["title"] and e["company"]
#         )
#         scores["experience"] = complete / len(result["experience"])
#     else:
#         scores["experience"] = 0.0

#     # Projects: high if at least one project has a name
#     if result["projects"]:
#         named = sum(1 for p in result["projects"] if p["name"])
#         scores["projects"] = named / len(result["projects"])
#     else:
#         scores["projects"] = 0.0

#     # Education: high only if every entry has both degree and institution
#     if result["education"]:
#         complete = sum(
#             1 for e in result["education"]
#             if e["degree"] and e["institution"]
#         )
#         scores["education"] = complete / len(result["education"])
#     else:
#         scores["education"] = 0.0

#     return scores
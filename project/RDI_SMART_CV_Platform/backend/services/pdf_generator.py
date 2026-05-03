def generate_cv_pdf(profile_data: dict, template: str = "Classic") -> bytes:
    """Generate a PDF from CV data. Uses WeasyPrint if available, else HTML fallback."""
    html = _build_cv_html(profile_data, template)
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except Exception:
        # Fallback: return the HTML itself (browser can print-to-PDF)
        return html.encode("utf-8")


def _build_cv_html(data: dict, template: str) -> str:
    name       = data.get("name", "")
    role       = data.get("role", "")
    email      = data.get("email", "")
    phone      = data.get("phone", "")
    location   = data.get("location", "")
    summary    = data.get("summary", "")
    skills     = data.get("skills", [])
    experience = data.get("experience", [])
    education  = data.get("education", [])

    # Template colour schemes
    themes = {
        "Modern Dark": {"bg": "#080810", "text": "#eeeef5", "accent": "#6affa0", "sub": "#8888aa", "divider": "#6affa0", "skill_bg": "#161625", "skill_border": "#252538", "skill_text": "#6affa0"},
        "Minimal":     {"bg": "#fafafa", "text": "#111",    "accent": "#333",    "sub": "#777",    "divider": "#ccc",    "skill_bg": "#f0f0f0", "skill_border": "#ddd",    "skill_text": "#444"},
        "Classic":     {"bg": "#ffffff", "text": "#111",    "accent": "#111",    "sub": "#666",    "divider": "#111",    "skill_bg": "#f3f3f3", "skill_border": "#e0e0e0", "skill_text": "#555"},
    }
    t = themes.get(template, themes["Classic"])

    exp_rows = ""
    for exp in experience:
        exp_rows += f"""
        <div style="margin-bottom:12px">
            <div style="font-weight:700;font-size:13px;color:{t['text']}">{exp.get('title','')}</div>
            <div style="color:{t['sub']};font-size:11px;margin-bottom:4px">
                {exp.get('company','')} &middot; {exp.get('period','')}
                {f" &middot; <em>{exp.get('type','')}</em>" if exp.get('type') else ''}
            </div>
            <div style="font-size:12px;color:{t['text']};line-height:1.6">{exp.get('description','')}</div>
        </div>"""

    edu_rows = ""
    for edu in education:
        edu_rows += f"""
        <div style="margin-bottom:10px">
            <div style="font-weight:700;font-size:13px;color:{t['text']}">{edu.get('degree','')}</div>
            <div style="color:{t['sub']};font-size:11px">
                {edu.get('institution','')} &middot; {edu.get('period','')}
                {f" &middot; <em>{edu.get('status','')}</em>" if edu.get('status') else ''}
            </div>
        </div>"""

    skills_html = "".join(
        f'<span style="background:{t["skill_bg"]};border:1px solid {t["skill_border"]};'
        f'padding:3px 10px;border-radius:4px;font-size:11px;margin:3px;'
        f'display:inline-block;color:{t["skill_text"]}">{s}</span>'
        for s in skills
    )

    def section(title, body):
        if not body.strip():
            return ""
        return f"""
        <div style="margin-bottom:18px">
            <div style="font-size:9px;text-transform:uppercase;letter-spacing:1.8px;
                        color:{t['sub']};margin-bottom:8px;font-weight:700">{title}</div>
            {body}
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  @page {{ margin: 20mm; }}
  body {{ font-family:'Helvetica Neue',Arial,sans-serif; background:{t['bg']}; color:{t['text']}; }}
</style>
</head>
<body>
<div style="max-width:700px;margin:0 auto;padding:32px">
  <h1 style="font-size:24px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;color:{t['text']}">{name}</h1>
  <div style="color:{t['sub']};font-size:13px;margin-bottom:8px">{role}</div>
  <div style="font-size:11px;color:{t['sub']};margin-bottom:20px">
    {" &nbsp;&middot;&nbsp; ".join(filter(None, [email, phone, location]))}
  </div>
  <div style="height:2px;background:linear-gradient(90deg,{t['divider']},transparent);margin-bottom:20px;border-radius:1px"></div>
  {section("About", f'<div style="font-size:13px;line-height:1.7;color:{t["text"]}">{summary}</div>')}
  {section("Experience", exp_rows)}
  {section("Education", edu_rows)}
  {section("Skills", f'<div style="line-height:2">{skills_html}</div>')}
</div>
</body>
</html>"""

import React from 'react';

export default function CVPreview({ data, template, onExportPDF, onExportDOCX }) {
  const { name, role, email, phone, location, summary, skills = [], experience = [] } = data;

  // Template-specific preview styles
  const templateStyles = {
    'Classic': {
      headerBg: '#ffffff',
      accentColor: '#111',
      bodyBg: '#ffffff',
    },
    'Modern Dark': {
      headerBg: 'linear-gradient(135deg,#0d1528,#080812)',
      accentColor: '#6affa0',
      bodyBg: '#080812',
    },
    'Minimal': {
      headerBg: '#fafafa',
      accentColor: '#333',
      bodyBg: '#fafafa',
    },
  };

  // const ts = templateStyles[template] || templateStyles['Classic']; // reserved for future template-specific preview styling

  return (
    <div className="cv-preview-wrap">
      <div className="cv-dl-bar">
        <button className="cv-dl-btn" onClick={onExportPDF}>Export PDF</button>
        <button className="cv-dl-btn" onClick={onExportDOCX}>Export DOCX</button>
      </div>
      <div className="cv-preview">
        <div className="cv-preview-toolbar">
          <div className="dot" style={{ background: '#ff5f57' }} />
          <div className="dot" style={{ background: '#ffbd2e' }} />
          <div className="dot" style={{ background: '#28c840' }} />
          <span style={{ fontSize: '.68rem', color: '#999', marginLeft: 8, fontFamily: "'DM Mono', monospace" }}>
            preview.pdf
          </span>
        </div>
        <div className="cv-preview-body" style={template === 'Modern Dark' ? { background: '#080812', color: '#eeeef5' } : {}}>
          <div className="cv-name">{name || 'Your Name'}</div>
          <div className="cv-role">{role || 'Your Role'}</div>
          <div className="cv-contact">
            {email && <span>{email}</span>}
            {phone && <span>{phone}</span>}
            {location && <span>{location}</span>}
          </div>
          <div className="cv-divider" style={template === 'Modern Dark' ? { background: 'linear-gradient(90deg,#6affa0,#4d9fff)' } : {}} />

          {summary && (
            <div className="cv-section">
              <div className="cv-sec-title">About</div>
              <div className="cv-about" style={template === 'Modern Dark' ? { color: '#aaaacc' } : {}}>{summary}</div>
            </div>
          )}

          {experience.length > 0 && (
            <div className="cv-section">
              <div className="cv-sec-title">Experience</div>
              {experience.map((exp, i) => (
                <div className="cv-exp-item" key={i}>
                  <div className="cv-exp-title">{exp.title}</div>
                  <div className="cv-exp-meta">{exp.company}{exp.period ? ` · ${exp.period}` : ''}</div>
                </div>
              ))}
            </div>
          )}

          {skills.length > 0 && (
            <div className="cv-section">
              <div className="cv-sec-title">Skills</div>
              <div className="cv-skills-row">
                {skills.map((s, i) => (
                  <span className="cv-skill" key={i}>{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

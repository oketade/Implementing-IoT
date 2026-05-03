import React, { useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import { calculateProfileStrength, generateInitials } from '../utils/helpers';

export default function ProfilePage({ showPage, showToast, profile, isProfileSaved, onOpenCompanyModal }) {
  const [strengthAnimated, setStrengthAnimated] = useState(false);
  const strengthRef = useRef(null);
  const [selectedTemplate, setSelectedTemplate] = useState('Classic');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    const el = strengthRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { setStrengthAnimated(true); obs.disconnect(); }
    }, { threshold: 0.3 });
    obs.observe(el);
    return () => obs.disconnect();
  }, [profile]);

  if (!isProfileSaved || !profile) {
    return (
      <div id="page-profile">
        <div className="container" style={{ textAlign: 'center', padding: '80px 20px' }}>
          <h2 style={{ marginBottom: 12 }}>No profile yet</h2>
          <p style={{ color: 'var(--ink2)', marginBottom: 28, maxWidth: 400, margin: '0 auto 28px' }}>
            Upload and save your CV to create your profile.
          </p>
          <button className="btn btn-primary" onClick={() => showPage('upload')}>Upload CV</button>
        </div>
      </div>
    );
  }

  const name      = profile.name     || '';
  const role      = profile.role     || '';
  const email     = profile.email    || '';
  const phone     = profile.phone    || '';
  const location  = profile.location || '';
  const github    = profile.github   || '';
  const linkedin  = profile.linkedin || '';
  const summary   = profile.summary  || '';
  const skills    = profile.skills   || [];
  const experience = profile.experience || [];
  const education  = profile.education  || [];
  const profileImage = profile.profileImage || null;

  const strengthScore = calculateProfileStrength(profile);
  const initials = generateInitials(name);

  const strengthTips = [];
  if (!linkedin)            strengthTips.push('Add a LinkedIn URL');
  if (skills.length < 5)   strengthTips.push('Add more skills');
  if (summary.length < 80) strengthTips.push('Write a longer summary');
  if (!profileImage)        strengthTips.push('Upload a profile photo');
  if (!experience.length)   strengthTips.push('Add work experience');

  const handleExportPDF = async () => {
    setExporting(true);
    try {
      const blob = await api.generatePDF(profile, selectedTemplate);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name.replace(/\s+/g, '_')}_cv.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('PDF downloaded!');
    } catch {
      showToast('PDF generation failed — try again');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div id="page-profile">
      {/* Hero */}
      <div className="profile-hero">
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, flexShrink: 0, position: 'relative', zIndex: 1 }}>
          <div className="profile-avatar" style={{ overflow: profileImage ? 'hidden' : 'visible', padding: profileImage ? 0 : undefined }}>
            {profileImage
              ? <img src={profileImage} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              : initials}
          </div>
        </div>

        <div className="profile-hero-info">
          <h1>{name}</h1>
          {role && <div className="role-badge">{role}</div>}
          {summary && <div className="bio">{summary}</div>}
        </div>
      </div>

      {/* Profile Strength */}
      <div className="profile-strength" ref={strengthRef}>
        <div className="strength-header">
          <div className="strength-label">Profile Strength</div>
          <div className="strength-pct">{strengthScore}%</div>
        </div>
        <div className="strength-bar">
          <div className="strength-fill" style={{ width: strengthAnimated ? `${strengthScore}%` : '0%' }} />
        </div>
        {strengthTips.length > 0 && (
          <div className="strength-tips">
            {strengthTips.map((tip, i) => <span key={i} className="strength-tip">{tip}</span>)}
          </div>
        )}
      </div>

      {/* Body */}
      <div className="profile-body">
        {/* Left Column */}
        <div>
          <div className="profile-card" style={{ marginBottom: 14 }}>
            <h3>Contact</h3>
            {email    && <div className="info-row"><span>{email}</span></div>}
            {location && <div className="info-row"><span>{location}</span></div>}
            {phone    && <div className="info-row"><span>{phone}</span></div>}
            {github   && <div className="info-row"><span>{github}</span></div>}
            {linkedin && <div className="info-row"><span>{linkedin}</span></div>}
          </div>

          {skills.length > 0 && (
            <div className="profile-card">
              <h3>Skills</h3>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginTop: 4 }}>
                {skills.map((s, i) => <span key={i} className="tag">{s}</span>)}
              </div>
            </div>
          )}
        </div>

        {/* Right Column */}
        <div>
          {experience.length > 0 && (
            <div className="profile-card" style={{ marginBottom: 14 }}>
              <h3>Experience</h3>
              {experience.map((exp, i) => (
                <div className="exp-card" key={i}>
                  <div>
                    <span className="exp-badge">{exp.type}</span>
                    <h4>{exp.title}</h4>
                  </div>
                  <div className="meta">{exp.company} · {exp.period}</div>
                  {exp.description && (
                    <p style={{ fontSize: '.78rem', color: 'var(--ink2)', marginTop: 6, lineHeight: 1.6 }}>
                      {exp.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}

          {education.length > 0 && (
            <div className="profile-card" style={{ marginBottom: 14 }}>
              <h3>Education</h3>
              {education.map((edu, i) => (
                <div className="exp-card" key={i}>
                  <div>
                    <span className="exp-badge">{edu.status}</span>
                    <h4>{edu.degree}</h4>
                  </div>
                  <div className="meta">{edu.institution} · {edu.period}</div>
                </div>
              ))}
            </div>
          )}

          {/* PDF Export */}
          <div className="profile-card" style={{ marginBottom: 14 }}>
            <h3>Export CV</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 12 }}>
              {['Classic', 'Modern Dark', 'Minimal', 'Tech Neon', 'Elegant'].map(tpl => (
                <button
                  key={tpl}
                  className={`btn btn-sm ${selectedTemplate === tpl ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setSelectedTemplate(tpl)}
                >
                  {tpl}
                </button>
              ))}
            </div>
            <button className="btn btn-primary" onClick={handleExportPDF} disabled={exporting}>
              {exporting ? 'Generating…' : 'Download PDF'}
            </button>
          </div>

          {/* Actions */}
          <div className="btn-row" style={{ marginTop: 4 }}>
            <button className="btn btn-secondary" onClick={() => showPage('builder')}>Edit in CV Builder</button>
            <button className="btn btn-ghost" onClick={onOpenCompanyModal}>Preview as Company</button>
          </div>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import AIEnhancePanel from '../components/AIEnhancePanel';
import CVPreview from '../components/CVPreview';
import { api } from '../api/client';
import { generateInitials, makeExperienceCRUD } from '../utils/helpers';

const ALL_SKILLS = [
  'Python', 'JavaScript', 'Node.js', 'React', 'SQL', 'IoT / MQTT',
  'Docker', 'TypeScript', 'PostgreSQL', 'AWS', 'Figma', 'Embedded C',
];

const BIO_TONES = ['Professional', 'Concise', 'Confident', 'Story-driven'];
const EXP_TONES = ['Impact-focused', 'Technical depth', 'Concise bullet'];
const EXP_TYPES = ['Full-time', 'Part-time', 'Internship', 'Contract', 'Freelance', 'Volunteer'];

const MOCK_SUMMARIES = {
  improve:   'Driven professional specializing in full-stack platform development. Proven ability to build scalable, data-driven applications that bridge engineering with real-world industry challenges.',
  rewrite:   'Results-oriented engineer with demonstrated expertise in modern web platform development. Adept at translating complex technical requirements into robust, production-ready solutions.',
  shorter:   'Full-stack developer focused on building data-driven applications that solve real industry problems.',
  impactful: 'Building the future of technology — one system at a time. Specializing in scalable platforms that turn raw data into actionable insights.',
};

const TEMPLATES = [
  { id: 'Classic',     label: 'Classic',     thumb: { background: 'linear-gradient(180deg,#ffffff 30px,#f7f7f5 100%)', border: '1px solid #e0e0e0' } },
  { id: 'Modern Dark', label: 'Modern Dark', thumb: { background: 'linear-gradient(135deg,#0d1528,#080812)' } },
  { id: 'Minimal',     label: 'Minimal',     thumb: { background: '#fafafa', border: '1px solid #ebebeb' } },
  { id: 'Tech Neon',   label: 'Tech Neon',   thumb: { background: 'linear-gradient(135deg,#0a0a1a,#001a0a)', border: '1px solid rgba(0,255,136,.25)' } },
  { id: 'Elegant',     label: 'Elegant',     thumb: { background: 'linear-gradient(180deg,#1a1208,#2d1f0a)', border: '1px solid rgba(201,168,76,.25)' } },
];

export default function BuilderPage({ showPage, showToast, cvData, setCvData, onSaveProfile }) {
  const [selectedTemplate, setSelectedTemplate] = useState('Classic');
  const [aiLoading, setAiLoading] = useState(false);
  const [customSkillInput, setCustomSkillInput] = useState('');

  const { addExperience, updateExperience, deleteExperience } = makeExperienceCRUD(setCvData);

  if (!cvData) {
    return (
      <div id="page-builder">
        <div className="container">
          <div className="page-header">
            <div className="page-title">CV Builder</div>
            <div className="page-sub">Craft a professional CV with AI writing assistance.</div>
          </div>
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <h3 style={{ marginBottom: 8 }}>No CV data yet</h3>
            <p style={{ color: 'var(--ink2)', marginBottom: 24 }}>Upload your CV first to use the builder.</p>
            <button className="btn btn-primary" onClick={() => showPage('upload')}>Go to CV Import</button>
          </div>
        </div>
      </div>
    );
  }

  const setField = (key, val) => setCvData(prev => ({ ...prev, [key]: val }));

  const toggleSkill = (skill) => {
    const skills = cvData.skills || [];
    setCvData(prev => ({
      ...prev,
      skills: skills.includes(skill) ? skills.filter(s => s !== skill) : [...skills, skill],
    }));
  };

  const addCustomSkill = () => {
    const val = customSkillInput.trim();
    if (val && !(cvData.skills || []).includes(val)) {
      setCvData(prev => ({ ...prev, skills: [...(prev.skills || []), val] }));
      showToast(`Added: ${val}`);
    }
    setCustomSkillInput('');
  };

  const handleAIWrite = async (type) => {
    const mockText = MOCK_SUMMARIES[type];
    setAiLoading(true);
    try {
      const toneMap = { improve: 'professional', rewrite: 'professional', shorter: 'concise', impactful: 'confident' };
      const data = await api.enhanceText(cvData.summary || '', toneMap[type] || 'professional');
      setField('summary', data.enhanced_text || mockText);
    } catch {
      setField('summary', mockText);
    } finally {
      setAiLoading(false);
      showToast('AI has rewritten your summary');
    }
  };

  const handleExportPDF = async () => {
    try {
      const blob = await api.generatePDF(cvData, selectedTemplate);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${(cvData.name || 'cv').replace(/\s+/g, '_')}_cv.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('PDF downloaded!');
    } catch {
      showToast('PDF generation failed — try again');
    }
  };

  const handleSaveProfile = async () => {
    try {
      await api.saveProfile({ name: cvData.name, email: cvData.email, final_data: cvData });
      showToast('Profile saved successfully!');
    } catch {
      showToast('Saved locally — server unreachable');
    }
    onSaveProfile(cvData);
    showPage('profile');
  };

  const initials = generateInitials(cvData.name || '');
  const customSkills = (cvData.skills || []).filter(s => !ALL_SKILLS.includes(s));
  const previewData = cvData;

  return (
    <div id="page-builder">
      <div className="container" style={{ maxWidth: 1100 }}>
        <div className="page-header">
          <div className="page-title">CV Builder</div>
          <div className="page-sub">Craft a professional CV with AI writing assistance. Changes update the preview in real time.</div>
        </div>

        {/* Template Picker */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="section-title">Choose a Template</div>
          <div className="tpl-picker">
            {TEMPLATES.map(tpl => (
              <div
                key={tpl.id}
                className={`tpl-card${selectedTemplate === tpl.id ? ' selected' : ''}`}
                onClick={() => { setSelectedTemplate(tpl.id); showToast(`Template "${tpl.id}" applied`); }}
              >
                <div className="tpl-thumb" style={tpl.thumb} />
                <div className="tpl-label">{tpl.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="builder-wrap">
          {/* Left: Form */}
          <div className="builder-form">

            {/* Profile Photo */}
            <div className="card">
              <div className="section-title">Profile Photo</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div className="profile-avatar" style={{ width: 56, height: 56, fontSize: '1.2rem', flexShrink: 0, overflow: cvData.profileImage ? 'hidden' : 'visible', padding: cvData.profileImage ? 0 : undefined }}>
                  {cvData.profileImage
                    ? <img src={cvData.profileImage} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                    : initials}
                </div>
                <p style={{ fontSize: '.78rem', color: 'var(--ink2)' }}>
                  {cvData.profileImage ? 'Photo uploaded' : `Showing initials: ${initials}. Upload a photo in CV Import.`}
                </p>
              </div>
            </div>

            {/* Personal Details */}
            <div className="card">
              <div className="section-title">Personal Details</div>
              <div className="grid-2">
                <div className="field">
                  <label>Full Name</label>
                  <input value={cvData.name || ''} onChange={e => setField('name', e.target.value)} />
                </div>
                <div className="field">
                  <label>Title / Role</label>
                  <input value={cvData.role || ''} onChange={e => setField('role', e.target.value)} placeholder="e.g. Software Engineer" />
                </div>
                <div className="field">
                  <label>Email</label>
                  <input value={cvData.email || ''} onChange={e => setField('email', e.target.value)} />
                </div>
                <div className="field">
                  <label>Phone</label>
                  <input value={cvData.phone || ''} onChange={e => setField('phone', e.target.value)} />
                </div>
                <div className="field">
                  <label>Location</label>
                  <input value={cvData.location || ''} onChange={e => setField('location', e.target.value)} />
                </div>
                <div className="field">
                  <label>LinkedIn</label>
                  <input value={cvData.linkedin || ''} onChange={e => setField('linkedin', e.target.value)} placeholder="linkedin.com/in/..." />
                </div>
              </div>
              <div className="field full" style={{ marginTop: 14 }}>
                <label>Summary</label>
                <div className="enhance-wrap">
                  <textarea
                    value={cvData.summary || ''}
                    onChange={e => setField('summary', e.target.value)}
                    rows={3}
                    style={{ paddingBottom: 38, opacity: aiLoading ? 0.5 : 1, transition: 'opacity .3s', borderColor: aiLoading ? 'var(--purple)' : '' }}
                  />
                  <AIEnhancePanel
                    panelId="bio-builder"
                    title="AI Bio Enhancement — choose a tone"
                    tones={BIO_TONES}
                    sourceText={cvData.summary || ''}
                    onApply={(text) => { setField('summary', text); showToast('Enhancement applied!'); }}
                  />
                </div>
                <div className="ai-writing-btns">
                  <button className="ai-write-btn" disabled={aiLoading} onClick={() => handleAIWrite('improve')}>Improve with AI</button>
                  <button className="ai-write-btn" disabled={aiLoading} onClick={() => handleAIWrite('rewrite')}>Rewrite professionally</button>
                  <button className="ai-write-btn" disabled={aiLoading} onClick={() => handleAIWrite('shorter')}>Make shorter</button>
                  <button className="ai-write-btn" disabled={aiLoading} onClick={() => handleAIWrite('impactful')}>More impactful</button>
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="card">
              <div className="section-title">Skills</div>
              <div className="skill-chips">
                {ALL_SKILLS.map(skill => (
                  <span key={skill} className={`chip${(cvData.skills || []).includes(skill) ? ' active' : ''}`} onClick={() => toggleSkill(skill)}>
                    {skill}
                  </span>
                ))}
              </div>
              {customSkills.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginTop: 10 }}>
                  {customSkills.map(skill => (
                    <span key={skill} className="tag tag-green">
                      {skill}
                      <span className="rm" onClick={() => setCvData(prev => ({ ...prev, skills: prev.skills.filter(s => s !== skill) }))}>&times;</span>
                    </span>
                  ))}
                </div>
              )}
              <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                <input
                  style={{ flex: 1, fontSize: '.82rem' }}
                  placeholder="Add custom skill…"
                  value={customSkillInput}
                  onChange={e => setCustomSkillInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addCustomSkill()}
                />
                <button className="btn btn-secondary btn-sm" onClick={addCustomSkill}>Add</button>
              </div>
            </div>

            {/* Experience */}
            <div className="card">
              <div className="section-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Experience
                <button className="btn btn-secondary btn-sm" onClick={addExperience}>+ Add</button>
              </div>
              {(cvData.experience || []).length === 0 && (
                <p style={{ color: 'var(--ink2)', fontSize: '.82rem' }}>No experience yet. Click "+ Add" to add one.</p>
              )}
              {(cvData.experience || []).map((exp, i) => (
                <div className="exp-card" key={i} style={{ position: 'relative' }}>
                  <button
                    onClick={() => deleteExperience(i)}
                    style={{ position: 'absolute', top: 8, right: 8, background: 'none', border: 'none', color: 'var(--ink2)', cursor: 'pointer', fontSize: '1rem', lineHeight: 1, padding: '2px 6px' }}
                    title="Remove"
                  >&times;</button>
                  <div className="grid-2" style={{ marginBottom: 8 }}>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Job Title</label>
                      <input value={exp.title || ''} onChange={e => updateExperience(i, 'title', e.target.value)} placeholder="e.g. Software Engineer" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Company</label>
                      <input value={exp.company || ''} onChange={e => updateExperience(i, 'company', e.target.value)} placeholder="e.g. Nokia" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Period</label>
                      <input value={exp.period || ''} onChange={e => updateExperience(i, 'period', e.target.value)} placeholder="e.g. Jan 2023 – Present" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Type</label>
                      <select value={exp.type || 'Full-time'} onChange={e => updateExperience(i, 'type', e.target.value)}>
                        {EXP_TYPES.map(t => <option key={t}>{t}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="exp-enhance-row">
                    <textarea
                      className="exp-desc"
                      placeholder="Describe your role and achievements…"
                      value={exp.description || ''}
                      onChange={e => updateExperience(i, 'description', e.target.value)}
                    />
                    <div style={{ marginTop: 6 }}>
                      <AIEnhancePanel
                        panelId={`exp-builder-${i}`}
                        title={`Enhance — ${exp.company || 'Experience'}`}
                        tones={EXP_TONES}
                        sourceText={exp.description || ''}
                        onApply={(text) => { updateExperience(i, 'description', text); showToast('Enhancement applied!'); }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Export & Save */}
            <div className="btn-row">
              <button className="btn btn-success" onClick={handleSaveProfile}>Save to Profile</button>
              <button className="btn btn-primary" onClick={handleExportPDF}>Export PDF</button>
              <button className="btn btn-secondary" onClick={() => showToast('DOCX export coming soon!')}>Export DOCX</button>
            </div>
          </div>

          {/* Right: Live Preview */}
          <CVPreview
            data={previewData}
            template={selectedTemplate}
            onExportPDF={handleExportPDF}
            onExportDOCX={() => showToast('DOCX export coming soon!')}
          />
        </div>
      </div>
    </div>
  );
}

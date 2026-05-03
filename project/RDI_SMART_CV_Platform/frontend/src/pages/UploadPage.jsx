import React, { useRef, useState } from 'react';
import AIEnhancePanel from '../components/AIEnhancePanel';
import { api } from '../api/client';
import { generateInitials, makeExperienceCRUD } from '../utils/helpers';

const BIO_TONES = ['Professional', 'Concise', 'Confident', 'Story-driven'];
const EXP_TONES = ['Impact-focused', 'Technical depth', 'Concise bullet'];
const DEFAULT_SUGGESTED = ['Docker', 'REST APIs', 'PostgreSQL', 'Git', 'Agile / Scrum', 'CI/CD'];
const EXP_TYPES = ['Full-time', 'Part-time', 'Internship', 'Contract', 'Freelance', 'Volunteer'];

export default function UploadPage({ showPage, showToast, cvData, setCvData, onSaveProfile }) {
  const fileInputRef = useRef(null);
  const photoInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadPhase, setUploadPhase] = useState('idle');
  const [progressText, setProgressText] = useState('');
  const [progressPct, setProgressPct] = useState(0);
  const [stepDone, setStepDone] = useState({ s1: false, s2: false, s3: false });
  const [stepActive, setStepActive] = useState('s1');
  const [stepLineDone, setStepLineDone] = useState({ sl1: false, sl2: false });
  const [suggestedSkills, setSuggestedSkills] = useState(DEFAULT_SUGGESTED);
  const [addedSuggestions, setAddedSuggestions] = useState(new Set());
  const [skillInput, setSkillInput] = useState('');

  // Experience CRUD
  const { addExperience, updateExperience, deleteExperience } = makeExperienceCRUD(setCvData);

  // CV field helpers
  const setField = (key, val) => setCvData(prev => ({ ...prev, [key]: val }));
  const setSkills = (fn) => setCvData(prev => ({ ...prev, skills: typeof fn === 'function' ? fn(prev?.skills || []) : fn }));

  // Profile photo upload
  const handlePhotoChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setCvData(prev => ({ ...prev, profileImage: ev.target.result }));
      showToast('Photo uploaded!');
    };
    reader.readAsDataURL(file);
  };

  // CV parse flow
  const runParse = async (file) => {
    setUploadPhase('uploading');
    const steps = [
      [300,  'Reading CV structure…',            25],
      [750,  'Extracting personal information…', 50],
      [1200, 'Detecting skills & keywords…',     75],
      [1700, 'Mapping fields to profile…',       100],
    ];
    steps.forEach(([t, txt, pct]) => setTimeout(() => { setProgressText(txt); setProgressPct(pct); }, t));

    let parsed = null;
    try {
      parsed = await api.uploadCV(file);
    } catch (err) {
      const msg = err?.message || '';
      if (msg.includes('422') || msg.toLowerCase().includes('extract')) {
        showToast('Could not read this PDF — try exporting your CV as .docx or .txt and uploading that');
      } else {
        showToast('Upload failed — check your connection and try again');
      }
    }

    setTimeout(async () => {
      if (!parsed) {
        setUploadPhase('idle');
        setProgressPct(0);
        setProgressText('');
        return;
      }

      setCvData(prev => ({
        ...(prev || {}),
        ...parsed,
        linkedin: parsed.linkedin || prev?.linkedin || '',
        github:   parsed.github   || prev?.github   || '',
        profileImage: prev?.profileImage || null,
      }));

      setUploadPhase('parsed');
      setStepDone(s => ({ ...s, s1: true }));
      setStepActive('s2');
      setStepLineDone(s => ({ ...s, sl1: true }));
      showToast('CV parsed! Review your details below.');

      try {
        const sugg = await api.suggestSkills(parsed);
        setSuggestedSkills(sugg.suggested_skills || DEFAULT_SUGGESTED);
      } catch {
        setSuggestedSkills(DEFAULT_SUGGESTED);
      }
    }, 2100);
  };

  const handleFileChange = (e) => { const f = e.target.files?.[0]; if (f) runParse(f); };
  const handleDrop = (e) => { e.preventDefault(); setIsDragging(false); const f = e.dataTransfer.files?.[0]; if (f) runParse(f); };

  // Skills management
  const removeSkill = (skill) => setSkills(s => s.filter(x => x !== skill));
  const handleSkillKeyDown = (e) => {
    if (e.key !== 'Enter') return;
    const val = skillInput.trim();
    if (val && !(cvData?.skills || []).includes(val)) {
      setSkills(s => [...s, val]);
      showToast(`Added: ${val}`);
    }
    setSkillInput('');
  };
  const acceptSuggested = (skill) => {
    if (addedSuggestions.has(skill)) return;
    setAddedSuggestions(s => new Set([...s, skill]));
    setSkills(s => s.includes(skill) ? s : [...s, skill]);
    showToast(`AI skill added: ${skill}`);
  };
  const acceptAllSuggested = () => {
    const toAdd = suggestedSkills.filter(s => !addedSuggestions.has(s));
    setAddedSuggestions(s => new Set([...s, ...toAdd]));
    setSkills(s => { const ex = new Set(s); return [...s, ...toAdd.filter(x => !ex.has(x))]; });
    showToast('All suggested skills added!');
  };

  // Save to profile (only here does data go to backend)
  const handleSaveProfile = async () => {
    if (!cvData) return;
    setStepDone(s => ({ ...s, s2: true }));
    setStepActive('s3');
    setStepLineDone(s => ({ ...s, sl2: true }));
    setTimeout(() => setStepDone(s => ({ ...s, s3: true })), 400);

    try {
      await api.saveProfile({ name: cvData.name, email: cvData.email, final_data: cvData });
      showToast('Profile saved successfully!');
    } catch {
      showToast('Saved locally — server unreachable');
    }

    onSaveProfile(cvData);
    setTimeout(() => showPage('profile'), 1200);
  };

  const handleReset = () => {
    setUploadPhase('idle');
    setProgressPct(0); setProgressText('');
    setStepDone({ s1: false, s2: false, s3: false });
    setStepActive('s1');
    setStepLineDone({ sl1: false, sl2: false });
    setSuggestedSkills(DEFAULT_SUGGESTED);
    setAddedSuggestions(new Set());
    setCvData(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const stepClass = (id) => stepDone[id] ? 'step-item done' : stepActive === id ? 'step-item active' : 'step-item';

  const initials = generateInitials(cvData?.name || '');
  const showReview = uploadPhase === 'parsed' || (cvData && uploadPhase === 'idle');

  return (
    <div id="page-upload">
      <div className="container">
        <div className="page-header">
          <div className="page-title">Import Your CV</div>
          <div className="page-sub">Upload an existing CV and we'll auto-fill your profile using AI-powered parsing.</div>
        </div>

        {/* Step indicators */}
        <div className="steps">
          <div className={stepClass('s1')}><div className="step-num">1</div><div className="step-label">Upload</div></div>
          <div className={`step-line${stepLineDone.sl1 ? ' done' : ''}`} />
          <div className={stepClass('s2')}><div className="step-num">2</div><div className="step-label">Review</div></div>
          <div className={`step-line${stepLineDone.sl2 ? ' done' : ''}`} />
          <div className={stepClass('s3')}><div className="step-num">3</div><div className="step-label">Save to Profile</div></div>
        </div>

        {/* Hidden inputs */}
        <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt" style={{ display: 'none' }} onChange={handleFileChange} />
        <input ref={photoInputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handlePhotoChange} />

        {/* Upload Zone */}
        {!showReview && uploadPhase !== 'uploading' && (
          <div
            className={`upload-zone${isDragging ? ' dragging' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <div className="upload-icon"></div>
            <h3>Drop your CV here, or click to browse</h3>
            <p>AI will extract and organize your information automatically</p>
            <div className="format-chips">
              <span className="format-chip">.pdf</span>
              <span className="format-chip">.docx</span>
              <span className="format-chip">.txt</span>
            </div>
          </div>
        )}

        {/* Progress */}
        {uploadPhase === 'uploading' && (
          <div className="progress-wrap">
            <div className="progress-head"><span>{progressText}</span><span>{progressPct}%</span></div>
            <div className="progress-bar"><div className="progress-fill" style={{ width: `${progressPct}%` }} /></div>
          </div>
        )}

        {/* Review Section */}
        {showReview && (
          <div className="parsed-section" style={{ display: 'block' }}>
            <div className="alert alert-success">
              <div>
                <strong>CV parsed successfully!</strong>{' '}
                {cvData?.name || 'Profile'} detected and auto-filled. Review and edit below before saving.
              </div>
            </div>

            {/* Profile Photo */}
            <div className="card">
              <div className="section-title">Profile Photo</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <div
                  className="profile-avatar"
                  style={{ width: 64, height: 64, fontSize: '1.4rem', cursor: 'pointer', flexShrink: 0, overflow: cvData?.profileImage ? 'hidden' : 'visible', padding: cvData?.profileImage ? 0 : undefined }}
                  onClick={() => photoInputRef.current?.click()}
                >
                  {cvData?.profileImage
                    ? <img src={cvData.profileImage} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }} />
                    : initials}
                </div>
                <div>
                  <button className="btn btn-secondary btn-sm" onClick={() => photoInputRef.current?.click()}>
                    {cvData?.profileImage ? 'Change Photo' : 'Upload Photo'}
                  </button>
                  {cvData?.profileImage && (
                    <button className="btn btn-ghost btn-sm" style={{ marginLeft: 8 }} onClick={() => setCvData(prev => ({ ...prev, profileImage: null }))}>
                      Remove
                    </button>
                  )}
                  <p style={{ fontSize: '.74rem', color: 'var(--ink2)', marginTop: 6 }}>
                    {cvData?.profileImage ? 'Photo uploaded' : 'Click avatar or button to upload'}
                  </p>
                </div>
              </div>
            </div>

            {/* Personal Information */}
            <div className="card">
              <div className="section-title">Personal Information</div>
              <div className="grid-2">
                <div className="field">
                  <label>Full Name <span className="auto-badge">auto-filled</span></label>
                  <input type="text" className="auto-filled" value={cvData?.name || ''} onChange={e => setField('name', e.target.value)} />
                </div>
                <div className="field">
                  <label>Email <span className="auto-badge">auto-filled</span></label>
                  <input type="text" className="auto-filled" value={cvData?.email || ''} onChange={e => setField('email', e.target.value)} />
                </div>
                <div className="field">
                  <label>Phone <span className="auto-badge">auto-filled</span></label>
                  <input type="text" className="auto-filled" value={cvData?.phone || ''} onChange={e => setField('phone', e.target.value)} />
                </div>
                <div className="field">
                  <label>Location <span className="auto-badge">auto-filled</span></label>
                  <input type="text" className="auto-filled" value={cvData?.location || ''} onChange={e => setField('location', e.target.value)} />
                </div>
                <div className="field">
                  <label>LinkedIn</label>
                  <input type="text" placeholder="linkedin.com/in/your-profile" value={cvData?.linkedin || ''} onChange={e => setField('linkedin', e.target.value)} />
                </div>
                <div className="field">
                  <label>GitHub</label>
                  <input type="text" placeholder="github.com/username" value={cvData?.github || ''} onChange={e => setField('github', e.target.value)} />
                </div>
                <div className="field full">
                  <label>About / Summary <span className="auto-badge">auto-filled</span></label>
                  <div className="enhance-wrap">
                    <textarea
                      className="auto-filled"
                      style={{ borderColor: 'rgba(106,255,160,.4)', background: 'rgba(106,255,160,.04)', paddingBottom: 38 }}
                      value={cvData?.summary || ''}
                      onChange={e => setField('summary', e.target.value)}
                      rows={4}
                    />
                    <AIEnhancePanel
                      panelId="bio-upload"
                      title="AI Bio Enhancement — choose a tone"
                      tones={BIO_TONES}
                      sourceText={cvData?.summary || ''}
                      onApply={(text) => { setField('summary', text); showToast('Enhancement applied!'); }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="card">
              <div className="section-title">Skills Detected</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, alignItems: 'center' }}>
                {(cvData?.skills || []).map((skill) => (
                  <span key={skill} className="tag tag-green">
                    {skill}
                    <span className="rm" onClick={() => removeSkill(skill)}>&times;</span>
                  </span>
                ))}
                <input
                  style={{ border: 'none', background: 'transparent', outline: 'none', fontSize: '.82rem', fontFamily: 'inherit', width: 120, color: 'var(--ink)' }}
                  placeholder="+ Add skill"
                  value={skillInput}
                  onChange={e => setSkillInput(e.target.value)}
                  onKeyDown={handleSkillKeyDown}
                />
              </div>
            </div>

            {/* AI Skill Suggestions */}
            <div className="ai-box ai-shimmer" style={{ background: 'linear-gradient(135deg, rgba(167,139,250,0.07), rgba(77,159,255,0.07))', backgroundSize: '200% 100%', animation: 'aiShimmer 4s infinite', marginTop: 14 }}>
              <div className="ai-box-title">
                Suggested skills from your experience
                <span className="ai-badge">AI Suggested</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 7, marginBottom: 14 }}>
                {suggestedSkills.map((skill) => (
                  <span
                    key={skill}
                    className={`tag tag-ai${addedSuggestions.has(skill) ? ' added' : ''}`}
                    onClick={() => acceptSuggested(skill)}
                  >
                    {skill}
                  </span>
                ))}
              </div>
              <button className="btn btn-ai btn-sm" onClick={acceptAllSuggested}>+ Add all suggested skills</button>
            </div>

            {/* Experience */}
            <div className="card" style={{ marginTop: 14 }}>
              <div className="section-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                Experience
                <button className="btn btn-secondary btn-sm" onClick={addExperience}>+ Add</button>
              </div>
              {(cvData?.experience || []).length === 0 && (
                <p style={{ color: 'var(--ink2)', fontSize: '.82rem' }}>No experience entries yet. Click "+ Add" to add one.</p>
              )}
              {(cvData?.experience || []).map((exp, idx) => (
                <div className="exp-card" key={idx} style={{ position: 'relative' }}>
                  <button
                    onClick={() => deleteExperience(idx)}
                    style={{ position: 'absolute', top: 8, right: 8, background: 'none', border: 'none', color: 'var(--ink2)', cursor: 'pointer', fontSize: '1rem', lineHeight: 1, padding: '2px 6px' }}
                    title="Remove"
                  >&times;</button>
                  <div className="grid-2" style={{ marginBottom: 8 }}>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Job Title</label>
                      <input value={exp.title} onChange={e => updateExperience(idx, 'title', e.target.value)} placeholder="e.g. Software Engineer" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Company</label>
                      <input value={exp.company} onChange={e => updateExperience(idx, 'company', e.target.value)} placeholder="e.g. Nokia" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Period</label>
                      <input value={exp.period} onChange={e => updateExperience(idx, 'period', e.target.value)} placeholder="e.g. Jan 2023 – Present" />
                    </div>
                    <div className="field">
                      <label style={{ fontSize: '.72rem' }}>Type</label>
                      <select value={exp.type || 'Full-time'} onChange={e => updateExperience(idx, 'type', e.target.value)}>
                        {EXP_TYPES.map(t => <option key={t}>{t}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="exp-enhance-row">
                    <textarea
                      className="exp-desc"
                      placeholder="Describe your role and achievements…"
                      value={exp.description || ''}
                      onChange={e => updateExperience(idx, 'description', e.target.value)}
                    />
                    <div style={{ marginTop: 6 }}>
                      <AIEnhancePanel
                        panelId={`exp-upload-${idx}`}
                        title={`Enhance — ${exp.company || 'Experience'}`}
                        tones={EXP_TONES}
                        sourceText={exp.description || ''}
                        onApply={(text) => { updateExperience(idx, 'description', text); showToast('Enhancement applied!'); }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Education */}
            <div className="card">
              <div className="section-title">Education</div>
              {(cvData?.education || []).length === 0 && (
                <p style={{ color: 'var(--ink2)', fontSize: '.82rem' }}>No education entries detected.</p>
              )}
              {(cvData?.education || []).map((edu, idx) => (
                <div className="exp-card" key={idx} style={{ position: 'relative' }}>
                  <button
                    onClick={() => setCvData(prev => ({ ...prev, education: prev.education.filter((_, i) => i !== idx) }))}
                    style={{ position: 'absolute', top: 8, right: 8, background: 'none', border: 'none', color: 'var(--ink2)', cursor: 'pointer', fontSize: '1rem', lineHeight: 1, padding: '2px 6px' }}
                  >&times;</button>
                  <div><span className="exp-badge">{edu.status}</span><h4>{edu.degree} <span className="auto-badge">auto-filled</span></h4></div>
                  <div className="meta">{edu.institution} · {edu.period}</div>
                </div>
              ))}
            </div>

            {/* Actions */}
            <div className="btn-row">
              <button className="btn btn-success" onClick={handleSaveProfile}>Save to Profile</button>
              <button className="btn btn-secondary" onClick={() => showPage('builder')}>Edit in CV Builder</button>
              <button className="btn btn-danger" onClick={handleReset}>Upload Another CV</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

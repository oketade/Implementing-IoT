import React from 'react';

export default function CompanyModal({ open, onClose, profileData }) {
  if (!profileData) return null;

  const initials = profileData.name
    ? profileData.name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    : 'PO';

  const role = profileData.role || profileData.final_data?.role || 'Professional';
  const location = profileData.location || profileData.final_data?.location || '';
  const summary = profileData.summary || profileData.final_data?.summary || '';
  const skills = profileData.skills || profileData.final_data?.skills || [];
  const name = profileData.name || '';

  return (
    <div
      className={`modal-overlay${open ? ' open' : ''}`}
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="modal-box">
        <button className="modal-close" onClick={onClose}>&times;</button>

        <div style={{ textAlign: 'center', marginBottom: 22 }}>
          <div style={{ display: 'inline-flex', padding: '4px 14px', borderRadius: 20, background: 'var(--amber-lt)', color: 'var(--amber)', fontSize: '.72rem', fontWeight: 600, border: '1px solid rgba(251,191,36,0.2)' }}>
            Company View
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: 'linear-gradient(135deg,var(--accent),var(--blue))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: '1.1rem', color: '#080810' }}>
            {initials}
          </div>
          <div>
            <div style={{ fontFamily: "'Syne', sans-serif", fontWeight: 800, fontSize: '1.15rem' }}>{name}</div>
            <div style={{ color: 'var(--ink2)', fontSize: '.84rem' }}>
              {role}{location ? ` · ${location}` : ''}
            </div>
          </div>
        </div>

        {summary && (
          <div style={{ fontSize: '.84rem', color: 'var(--ink2)', lineHeight: 1.6, marginBottom: 18 }}>
            {summary}
          </div>
        )}

        {skills.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 18 }}>
            {skills.map((s, i) => (
              <span key={i} className="tag" style={{ fontSize: '.72rem' }}>{s}</span>
            ))}
          </div>
        )}

        <div style={{ fontSize: '.76rem', color: 'var(--ink3)', textAlign: 'center', paddingTop: 16, borderTop: '1px solid var(--border)' }}>
          This is how your profile appears to companies on the RDI platform.
        </div>
      </div>
    </div>
  );
}

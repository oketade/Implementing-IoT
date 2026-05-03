import React, { useState } from 'react';
import { api } from '../api/client';

const MOCK_ENHANCED = {
  professional:    "Results-driven professional with demonstrated expertise and a proven track record of delivering high-impact solutions. Skilled at translating complex challenges into practical, scalable outcomes.",
  concise:         "Experienced professional skilled in delivering practical solutions. Strong technical background with a focus on real-world results.",
  confident:       "A driven and ambitious professional who consistently delivers outstanding results. Ready to take on complex challenges and lead initiatives that make a measurable impact.",
  'story-driven':  "My journey began with a curiosity for how technology shapes industries. Today, I channel that passion into building solutions that bridge engineering with real-world problems.",
  'impact-focused':"Delivered key contributions that improved team efficiency and output quality. Collaborated closely with senior stakeholders to meet project goals on time.",
  'technical depth':"Architected scalable backend services using modern frameworks. Implemented clean REST APIs, managed relational databases, and maintained CI/CD pipelines.",
  'concise bullet': "• Delivered core features and improvements to production systems\n• Collaborated with cross-functional teams to meet deadlines\n• Maintained code quality through reviews and testing",
};

export default function AIEnhancePanel({ panelId, title, tones, sourceText, onApply, onClose }) {
  const [open, setOpen] = useState(false);
  const [selectedTone, setSelectedTone] = useState(null);
  const [loading, setLoading] = useState(false);
  const [enhancedText, setEnhancedText] = useState('');
  const [showResult, setShowResult] = useState(false);

  const handleToggle = () => {
    if (open) {
      handleClose();
    } else {
      setOpen(true);
    }
  };

  const handlePickTone = async (tone) => {
    setSelectedTone(tone);
    setShowResult(true);
    setLoading(true);
    setEnhancedText('');

    try {
      const data = await api.enhanceText(sourceText || '', tone);
      setEnhancedText(data.enhanced_text || MOCK_ENHANCED[tone.toLowerCase()] || '');
    } catch {
      setEnhancedText(MOCK_ENHANCED[tone.toLowerCase()] || sourceText || '');
    } finally {
      setLoading(false);
    }
  };

  const handleRegen = () => {
    if (selectedTone) handlePickTone(selectedTone);
  };

  const handleApply = () => {
    if (enhancedText && !loading) {
      onApply(enhancedText);
      handleClose();
    }
  };

  const handleClose = () => {
    setOpen(false);
    setShowResult(false);
    setSelectedTone(null);
    setEnhancedText('');
    if (onClose) onClose();
  };

  return (
    <>
      <button className="ai-btn ai-btn-inline" onClick={handleToggle}>
        Enhance with AI
      </button>

      <div className={`enhance-panel${open ? ' open' : ''}`}>
        <div className="ep-header">{title}</div>
        <div className="ep-tones">
          {tones.map((tone) => (
            <button
              key={tone}
              className={`tone-btn${selectedTone === tone ? ' sel' : ''}`}
              onClick={() => handlePickTone(tone)}
            >
              {tone}
            </button>
          ))}
        </div>

        <div className={`ep-result${showResult ? ' show' : ''}`}>
          <div className="ep-result-head">
            <span>Enhanced version</span>
            <span style={{ opacity: 0.7, fontWeight: 400 }}>{selectedTone}</span>
          </div>
          <div className={`ep-result-body${loading ? ' loading' : ''}`}>
            {loading ? (
              <>AI is writing your enhanced version…<span className="stream-cursor" /></>
            ) : (
              enhancedText.split('\n').map((line, i) => (
                <React.Fragment key={i}>{line}{i < enhancedText.split('\n').length - 1 && <br />}</React.Fragment>
              ))
            )}
          </div>
          <div className="ep-actions">
            <button className="ep-act ep-apply" onClick={handleApply} disabled={loading}>
              Apply
            </button>
            <button className="ep-act ep-regen" onClick={handleRegen} disabled={loading}>
              Retry
            </button>
            <button className="ep-act ep-discard" onClick={handleClose}>
              &times;
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

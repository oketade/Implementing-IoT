import React from 'react';

const SCREEN_NAMES = {
  upload:  '01 · CV Import',
  builder: '02 · CV Builder',
  profile: '03 · Profile',
};

export default function ProtoBar({ currentPage, showPage }) {
  return (
    <div className="proto-bar">
      <span className="label">PROTOTYPE</span>
      <span className="divider" />
      <span className="label">RDI Platform&nbsp;/</span>
      <span className="screen-name">{SCREEN_NAMES[currentPage]}</span>
      <span className="divider" />
      <div className="flow-steps">
        <button
          className={`proto-step${currentPage === 'upload' ? ' current' : ''}`}
          onClick={() => showPage('upload')}
        >
          <span className="dot" />Import
        </button>
        <button
          className={`proto-step${currentPage === 'builder' ? ' current' : ''}`}
          onClick={() => showPage('builder')}
        >
          <span className="dot" />Builder
        </button>
        <button
          className={`proto-step${currentPage === 'profile' ? ' current' : ''}`}
          onClick={() => showPage('profile')}
        >
          <span className="dot" />Profile
        </button>
      </div>
    </div>
  );
}

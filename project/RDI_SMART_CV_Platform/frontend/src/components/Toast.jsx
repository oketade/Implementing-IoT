import React from 'react';

export default function Toast({ visible, message }) {
  return (
    <div className={`toast${visible ? ' show' : ''}`}>
      <span>{message}</span>
    </div>
  );
}

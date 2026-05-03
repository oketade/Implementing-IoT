// import React from 'react';

// export default function Navbar({
//   currentPage,
//   showPage,
//   onLogoClick,
//   profileStrength,
//   profileName,
//   hasProfile,
// }) {
//   // Build initials from name (up to 2 chars), fall back to empty string
//   const initials = profileName
//     ? profileName.split(' ').filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase()
//     : '';

//   const handleAvatarClick = () => {
//     if (hasProfile) showPage('profile');
//   };

//   const handleProfileNavClick = () => showPage('profile');

//   return (
//     <nav>
//       {/* Logo — smart navigation */}
//       <div className="nav-logo" onClick={onLogoClick} role="button" tabIndex={0}
//            onKeyDown={e => e.key === 'Enter' && onLogoClick()}>
//         RDI<span>.</span>
//       </div>

//       {/* Pill nav tabs */}
//       <div className="nav-links">
//         <button
//           className={`nav-link${currentPage === 'upload' ? ' active' : ''}`}
//           onClick={() => showPage('upload')}
//         >
//           CV Import
//         </button>
//         <button
//           className={`nav-link${currentPage === 'builder' ? ' active' : ''}`}
//           onClick={() => showPage('builder')}
//         >
//           CV Builder
//         </button>
//         <button
//           className={`nav-link${currentPage === 'profile' ? ' active' : ''}`}
//           onClick={handleProfileNavClick}
//         >
//           My Profile
//         </button>
//       </div>

//       {/* Right section */}
//       <div className="nav-right">
//         {/* Profile strength bar — only show when profile exists */}
//         {hasProfile && (
//           <div className="nav-strength">
//             <span style={{ fontSize: '.72rem', color: 'var(--ink3)' }}>Profile</span>
//             <div className="nav-strength-bar">
//               <div className="nav-strength-fill" style={{ width: `${profileStrength}%` }} />
//             </div>
//             <span style={{ fontWeight: 600, fontSize: '.78rem', color: 'var(--accent)' }}>
//               {profileStrength}%
//             </span>
//           </div>
//         )}

//         {/* Avatar — initials if profile exists, generic icon if not */}
//         <div
//           className="avatar"
//           onClick={handleAvatarClick}
//           title={profileName ? `${profileName}${hasProfile ? ' — view profile' : ''}` : 'No profile yet'}
//           role={hasProfile ? 'button' : 'img'}
//           tabIndex={hasProfile ? 0 : -1}
//           onKeyDown={e => e.key === 'Enter' && hasProfile && handleAvatarClick()}
//           style={!hasProfile ? { opacity: 0.45, cursor: 'default' } : {}}
//         >
//           {initials || '?'}
//         </div>
//       </div>
//     </nav>
//   );
// }
import React from 'react';

export default function Navbar({
  currentPage,
  showPage,
  onLogoClick,
  profileStrength,
  profileName,
  hasProfile,

  // ✅ NEW (from App)
  theme,
  setTheme,
}) {
  const initials = profileName
    ? profileName.split(' ').filter(Boolean).map(w => w[0]).join('').slice(0, 2).toUpperCase()
    : '';

  const handleAvatarClick = () => {
    if (hasProfile) showPage('profile');
  };

  const handleProfileNavClick = () => showPage('profile');

  return (
    <nav>
      {/* Logo */}
      <div
        className="nav-logo"
        onClick={onLogoClick}
        role="button"
        tabIndex={0}
        onKeyDown={e => e.key === 'Enter' && onLogoClick()}
      >
        RDI<span>.</span>
      </div>

      {/* Navigation */}
      <div className="nav-links">
        <button
          className={`nav-link${currentPage === 'upload' ? ' active' : ''}`}
          onClick={() => showPage('upload')}
        >
          CV Import
        </button>

        <button
          className={`nav-link${currentPage === 'builder' ? ' active' : ''}`}
          onClick={() => showPage('builder')}
        >
          CV Builder
        </button>

        <button
          className={`nav-link${currentPage === 'profile' ? ' active' : ''}`}
          onClick={handleProfileNavClick}
        >
          My Profile
        </button>
      </div>

      {/* Right section */}
      <div className="nav-right">

        {/* 🌗 THEME TOGGLE BUTTON */}
        <button
          className="btn btn-ghost"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title="Toggle theme"
        >
          {theme === 'dark' ? '🌞' : '🌙'}
        </button>

        {/* Profile strength */}
        {hasProfile && (
          <div className="nav-strength">
            <span style={{ fontSize: '.72rem', color: 'var(--ink3)' }}>
              Profile
            </span>
            <div className="nav-strength-bar">
              <div
                className="nav-strength-fill"
                style={{ width: `${profileStrength}%` }}
              />
            </div>
            <span
              style={{
                fontWeight: 600,
                fontSize: '.78rem',
                color: 'var(--accent)',
              }}
            >
              {profileStrength}%
            </span>
          </div>
        )}

        {/* Avatar */}
        <div
          className="avatar"
          onClick={handleAvatarClick}
          title={
            profileName
              ? `${profileName}${hasProfile ? ' — view profile' : ''}`
              : 'No profile yet'
          }
          role={hasProfile ? 'button' : 'img'}
          tabIndex={hasProfile ? 0 : -1}
          onKeyDown={e =>
            e.key === 'Enter' && hasProfile && handleAvatarClick()
          }
          style={!hasProfile ? { opacity: 0.45, cursor: 'default' } : {}}
        >
          {initials || '?'}
        </div>
      </div>
    </nav>
  );
}
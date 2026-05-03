// import React, { useState, useCallback, useEffect, useRef } from 'react';
// import './styles/globals.css';
// import Navbar from './components/Navbar';
// import Toast from './components/Toast';
// import CompanyModal from './components/CompanyModal';
// import UploadPage from './pages/UploadPage';
// import BuilderPage from './pages/BuilderPage';
// import ProfilePage from './pages/ProfilePage';
// import { calculateProfileStrength } from './utils/helpers';

// export default function App() {
//   const [currentPage, setCurrentPage] = useState('upload');
//   const [toast, setToast] = useState({ visible: false, message: '' });
//   const toastTimerRef = useRef(null);

//   // Single source of truth — never persisted, always starts fresh on refresh
//   const [cvData, setCvData] = useState(null);
//   const [profile, setProfile] = useState(null);
//   const [isProfileSaved, setIsProfileSaved] = useState(false);

//   const profileRef = useRef(profile);
//   useEffect(() => { profileRef.current = profile; }, [profile]);

//   const [companyModalOpen, setCompanyModalOpen] = useState(false);

//   const showToast = useCallback((message, duration = 3000) => {
//     if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
//     setToast({ visible: true, message });
//     toastTimerRef.current = setTimeout(() => setToast({ visible: false, message: '' }), duration);
//   }, []);

//   const showPage = useCallback((page) => {
//     if (page === 'profile' && !profileRef.current) {
//       showToast('Upload and save your CV first to view your profile');
//       return;
//     }
//     setCurrentPage(page);
//     window.scrollTo({ top: 0, behavior: 'smooth' });
//   }, [showToast]);

//   const handleLogoClick = useCallback(() => {
//     setCurrentPage(profileRef.current ? 'profile' : 'upload');
//     window.scrollTo({ top: 0, behavior: 'smooth' });
//   }, []);

//   const handleSaveProfile = useCallback((savedData) => {
//     setProfile(savedData);
//     setIsProfileSaved(true);
//   }, []);

//   const profileStrength = calculateProfileStrength(profile || cvData);

//   return (
//     <>
//       <div className="app">
//         <Navbar
//           currentPage={currentPage}
//           showPage={showPage}
//           onLogoClick={handleLogoClick}
//           profileStrength={profileStrength}
//           profileName={profile?.name || cvData?.name || ''}
//           hasProfile={isProfileSaved}
//         />

//         <div className={`page${currentPage === 'upload' ? ' active' : ''}`}>
//           <UploadPage
//             showPage={showPage}
//             showToast={showToast}
//             cvData={cvData}
//             setCvData={setCvData}
//             onSaveProfile={handleSaveProfile}
//           />
//         </div>

//         <div className={`page${currentPage === 'builder' ? ' active' : ''}`}>
//           <BuilderPage
//             showPage={showPage}
//             showToast={showToast}
//             cvData={cvData}
//             setCvData={setCvData}
//             onSaveProfile={handleSaveProfile}
//           />
//         </div>

//         <div className={`page${currentPage === 'profile' ? ' active' : ''}`}>
//           <ProfilePage
//             showPage={showPage}
//             showToast={showToast}
//             profile={profile}
//             isProfileSaved={isProfileSaved}
//             onOpenCompanyModal={() => setCompanyModalOpen(true)}
//           />
//         </div>
//       </div>

//       <Toast visible={toast.visible} message={toast.message} />

//       <CompanyModal
//         open={companyModalOpen}
//         onClose={() => setCompanyModalOpen(false)}
//         profileData={profile}
//       />
//     </>
//   );
// }


import React, { useState, useCallback, useEffect, useRef } from 'react';
import './styles/globals.css';
import Navbar from './components/Navbar';
import Toast from './components/Toast';
import CompanyModal from './components/CompanyModal';
import UploadPage from './pages/UploadPage';
import BuilderPage from './pages/BuilderPage';
import ProfilePage from './pages/ProfilePage';
import { calculateProfileStrength } from './utils/helpers';

/* ✅ THEME HOOK (SAFE VERSION) */
function useTheme() {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem("theme") || "dark";
    } catch {
      return "dark";
    }
  });

  useEffect(() => {
    if (theme === "light") {
      document.body.classList.add("light");
    } else {
      document.body.classList.remove("light");
    }

    try {
      localStorage.setItem("theme", theme);
    } catch {}
  }, [theme]);

  return { theme, setTheme };
}

export default function App() {
  const { theme, setTheme } = useTheme();

  const [currentPage, setCurrentPage] = useState('upload');
  const [toast, setToast] = useState({ visible: false, message: '' });
  const toastTimerRef = useRef(null);

  // Single source of truth
  const [cvData, setCvData] = useState(null);
  const [profile, setProfile] = useState(null);
  const [isProfileSaved, setIsProfileSaved] = useState(false);

  const profileRef = useRef(profile);
  useEffect(() => {
    profileRef.current = profile;
  }, [profile]);

  const [companyModalOpen, setCompanyModalOpen] = useState(false);

  /* ✅ FIXED TOAST (with cleanup-safe logic) */
  const showToast = useCallback((message, duration = 3000) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);

    setToast({ visible: true, message });

    toastTimerRef.current = setTimeout(() => {
      setToast({ visible: false, message: '' });
    }, duration);
  }, []);

  /* ✅ CLEANUP (prevents memory leak) */
  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

  const showPage = useCallback((page) => {
    if (page === 'profile' && !profileRef.current) {
      showToast('Upload and save your CV first to view your profile');
      return;
    }
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [showToast]);

  const handleLogoClick = useCallback(() => {
    setCurrentPage(profileRef.current ? 'profile' : 'upload');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const handleSaveProfile = useCallback((savedData) => {
    setProfile(savedData);
    setIsProfileSaved(true);
  }, []);

  const profileStrength = calculateProfileStrength(profile || cvData);

  return (
    <>
      <div className="app">
        <Navbar
          currentPage={currentPage}
          showPage={showPage}
          onLogoClick={handleLogoClick}
          profileStrength={profileStrength}
          profileName={profile?.name || cvData?.name || ''}
          hasProfile={isProfileSaved}
          theme={theme}
          setTheme={setTheme}
        />

        <div className={`page${currentPage === 'upload' ? ' active' : ''}`}>
          <UploadPage
            showPage={showPage}
            showToast={showToast}
            cvData={cvData}
            setCvData={setCvData}
            onSaveProfile={handleSaveProfile}
          />
        </div>

        <div className={`page${currentPage === 'builder' ? ' active' : ''}`}>
          <BuilderPage
            showPage={showPage}
            showToast={showToast}
            cvData={cvData}
            setCvData={setCvData}
            onSaveProfile={handleSaveProfile}
          />
        </div>

        <div className={`page${currentPage === 'profile' ? ' active' : ''}`}>
          <ProfilePage
            showPage={showPage}
            showToast={showToast}
            profile={profile}
            isProfileSaved={isProfileSaved}
            onOpenCompanyModal={() => setCompanyModalOpen(true)}
          />
        </div>
      </div>

      <Toast visible={toast.visible} message={toast.message} />

      <CompanyModal
        open={companyModalOpen}
        onClose={() => setCompanyModalOpen(false)}
        profileData={profile}
      />
    </>
  );
}
export function calculateProfileStrength(data) {
  if (!data) return 0;
  let score = 0;
  if (data.name) score += 10;
  if (data.email) score += 10;
  if (data.phone) score += 10;
  if (data.summary) score += 15;
  if (data.skills?.length) score += 15;
  if (data.experience?.length) score += 20;
  if (data.education?.length) score += 10;
  if (data.profileImage) score += 10;
  return Math.min(score, 100);
}

export function generateInitials(name) {
  if (!name) return '?';
  return name.split(' ').filter(Boolean).map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

export function makeExperienceCRUD(setCvData) {
  const addExperience = () =>
    setCvData(prev => ({
      ...prev,
      experience: [...(prev?.experience || []), { title: '', company: '', period: '', description: '', type: 'Full-time' }],
    }));

  const updateExperience = (idx, field, value) =>
    setCvData(prev => {
      const exps = [...(prev?.experience || [])];
      exps[idx] = { ...exps[idx], [field]: value };
      return { ...prev, experience: exps };
    });

  const deleteExperience = (idx) =>
    setCvData(prev => ({
      ...prev,
      experience: (prev?.experience || []).filter((_, i) => i !== idx),
    }));

  return { addExperience, updateExperience, deleteExperience };
}

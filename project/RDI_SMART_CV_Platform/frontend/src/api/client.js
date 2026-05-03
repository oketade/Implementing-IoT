const API_BASE = "http://localhost:8000";
async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `HTTP ${res.status}`);
  }
  return res;
}

export const api = {
  /**
   * Upload a CV file and receive parsed structured data.
   * @param {File} file
   * @returns {Promise<object>} ParsedCV
   */
  uploadCV: async (file) => {
    const form = new FormData();
    form.append('file', file);
    const res = await request('/upload-cv', { method: 'POST', body: form });
    return res.json();
  },

  /**
   * Enhance a text snippet using AI.
   * @param {string} text
   * @param {string} tone
   * @returns {Promise<{enhanced_text: string}>}
   */
  enhanceText: async (text, tone) => {
    const res = await request('/enhance-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, tone }),
    });
    return res.json();
  },

  /**
   * Get AI-suggested skills based on parsed CV data.
   * @param {object} parsedData
   * @returns {Promise<{suggested_skills: string[]}>}
   */
  suggestSkills: async (parsedData) => {
    const res = await request('/suggest-skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ parsed_data: parsedData }),
    });
    return res.json();
  },

  /**
   * Save a profile to the database.
   * @param {{name: string, email: string, final_data: object}} data
   * @returns {Promise<object>} ProfileResponse
   */
  saveProfile: async (data) => {
    const res = await request('/save-profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  /**
   * Fetch a profile by numeric ID.
   * @param {number} id
   * @returns {Promise<object>}
   */
  getProfile: async (id) => {
    const res = await request(`/profile/${id}`);
    return res.json();
  },

  /**
   * AI photo enhancement (mock-ready).
   * @param {string} name
   * @param {string} currentUrl
   * @returns {Promise<{enhanced_url: string, status: string, mock: boolean}>}
   */
  enhancePhoto: async (name = '', currentUrl = '') => {
    const res = await request('/enhance-photo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, current_url: currentUrl }),
    });
    return res.json();
  },

  /**
   * Generate and download a PDF of the CV.
   * @param {object} profileData
   * @param {string} template  "Classic" | "Modern Dark" | "Minimal"
   * @returns {Promise<Blob>}
   */
  generatePDF: async (profileData, template = 'Classic') => {
    const res = await request(`/generate-pdf?template=${encodeURIComponent(template)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData),
    });
    return res.blob();
  },
};

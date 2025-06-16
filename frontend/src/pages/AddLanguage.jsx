import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AddLanguage.css';

function AddLanguage() {
  const navigate = useNavigate();
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [error, setError] = useState(null);

  // Example list of languages — you can expand this or pull from an API later
  const languages = [
    'English',
    'Korean',
    'Hindi',
    'Spanish',
    'French',
    'Japanese',
    'Chinese',
    'German',
    'Italian',
    'Portuguese',
    'Arabic',
    'Russian',
  ];

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      navigate('/');
    } else {
      setToken(storedToken);
      setUser(storedUserId);
    }
  }, [navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!token || !selectedLanguage) return;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/addLanguage?user_id=${user}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          "language": selectedLanguage,
        }),
      });

      if (!response.ok) {
        if (response.status === 409) {
          throw new Error('You already added this language.');
        }
  
        const errorData = await response.json(); 
        throw new Error(errorData.message || 'Failed to add language.');
      }
  
      const data = await response.json(); 
      console.log('Language added:', data);
      navigate('/');
    } catch (err) {
      console.error(err);
      setError(`${err.message} Please try again.`);
    }
  }

  useEffect(() => {
    if (error) setError(null);
  }, [selectedLanguage]);
  

  return (
    <div className="add-language-container">
      <h2>Add a Language</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Choose a language:
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            required
          >
            <option value="">--Select Language--</option>
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {lang}
              </option>
            ))}
          </select>
        </label>
        <div className="button-group">
            <button
                type="submit"
                className="submit-button"
                disabled={!selectedLanguage}
            >
                Add Language
            </button>
            <button
                type="button"
                className="cancel-button"
                onClick={() => navigate(`/`)}
            >
                Cancel
            </button>
        </div>
      </form>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default AddLanguage;

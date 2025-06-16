import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/AddFlashcard.css';

function AddFlashcard() {
  const { language_id, set_id } = useParams();
  const navigate = useNavigate();

  const [word, setWord] = useState('');
  const [usage, setUsage] = useState('');
  const [translatedWord, setTranslatedWord] = useState('');
  const [translatedUsage, setTranslatedUsage] = useState('');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUserId = localStorage.getItem('user_id');
    if (!storedToken) {
      navigate('/');
    } else {
      setUser(storedUserId);
      setToken(storedToken);
    }
  }, [navigate]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!token) return;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/addFlashcard?user_id=${user}&language=${language_id}&set_id=${set_id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            "word": word,
            "usage": usage,
            "translated_word": translatedWord,
            "translated_usage": translatedUsage,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to add flashcard.');
      }

      const data = await response.json();
      console.log('Flashcard added:', data);
      navigate(`/flashcard/${language_id}/${set_id}`); 
    } catch (err) {
      console.error(err);
      setError(err.message || 'Error adding flashcard. Please try again.');
    }
  }

  return (
    <div className="add-flashcard-container">
      <h2>Add New Flashcard</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Word:
          <input
            type="text"
            value={word}
            onChange={(e) => setWord(e.target.value)}
            required
          />
        </label>

        <label>
          Usage:
          <textarea
            value={usage}
            onChange={(e) => setUsage(e.target.value)}
            required
          />
        </label>

        <label>
          Translated Word:
          <input
            type="text"
            value={translatedWord}
            onChange={(e) => setTranslatedWord(e.target.value)}
            required
          />
        </label>

        <label>
          Translated Usage:
          <textarea
            value={translatedUsage}
            onChange={(e) => setTranslatedUsage(e.target.value)}
            required
          />
        </label>

        
        <div className="button-group">
            <button
                type="submit"
                className="submit-button"
                disabled={!word || !usage || !translatedWord || !translatedUsage}>
                    Add Flashcard
            </button>
            <button
                type="button"
                className="cancel-button"
                onClick={() => navigate(`/flashcard/${language_id}/${set_id}`)}
            >
                Cancel
            </button>
        </div>
      </form>

      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default AddFlashcard;


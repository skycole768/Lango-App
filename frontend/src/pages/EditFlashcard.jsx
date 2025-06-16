import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/EditFlashcard.css';

function EditFlashcard() {
  const { language_id, set_id, flashcard_id } = useParams();
  const navigate = useNavigate();

  const [word, setWord] = useState('');
  const [usage, setUsage] = useState('');
  const [translatedWord, setTranslatedWord] = useState('');
  const [translatedUsage, setTranslatedUsage] = useState('');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    const storedToken = localStorage.getItem('token');
    if (!storedToken) {
      navigate('/');
      return;
    }

    setToken(storedToken);
    setUser(storedUserId);
  
    async function fetchFlashcard() {
        try {
            const response = await fetch(
            `${import.meta.env.VITE_API_BASE_URL}/getFlashcard?user_id=${storedUserId}&language=${language_id}&set_id=${set_id}&flashcard_id=${flashcard_id}`,
            {
                method: 'GET',
                headers: {
                'Content-Type': 'application/json',
                },
            }
            );
    
            const data = await response.json();
            const flashcard = data.flashcard;
    
            setWord(flashcard.word || '');
            setUsage(flashcard.usage || '');
            setTranslatedWord(flashcard.translated_word || '');
            setTranslatedUsage(flashcard.translated_usage || '');
        } catch (err) {
            console.error(err);
            setError('Failed to load flashcard. Please try again.');
        }
        }
    
    fetchFlashcard();
  }, [navigate, language_id, set_id, flashcard_id]);
  
  // Submit updated flashcard
  async function handleSubmit(e) {
    e.preventDefault();
    if (!token) return;

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/editFlashcard?user_id=${user}&language=${language_id}&set_id=${set_id}&flashcard_id=${flashcard_id}`,
        {
          method: 'PUT',
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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to update flashcard.');
      }

      const data = await response.json();
      console.log('Flashcard updated:', data);
      navigate(`/flashcard/${language_id}/${set_id}`);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Error updating flashcard. Please try again.');
    }
  }

  return (
    <div className="edit-flashcard-container">
      <h2>Edit Flashcard</h2>
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
            className="submit-button"
            type="submit"
            disabled={!word || !usage || !translatedWord || !translatedUsage}
            >
            Update Flashcard
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

export default EditFlashcard;

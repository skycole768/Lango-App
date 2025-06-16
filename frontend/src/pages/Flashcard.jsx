import React, { useState, useEffect } from 'react';
import { useNavigate, useParams} from 'react-router-dom';
import FlashcardCard from '../components/FlashcardCard';
import '../styles/Flashcard.css';

function Flashcard() {
  const [flashcards, setFlashcards] = useState([]);
  const navigate = useNavigate();
  const { set_id, language_id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  
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

  useEffect(() => {
      // Fetch flashcard data from the server
      const fetchFlashcards = async () => {
        if (!token) return;
          try {
              const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/getFlashcards?user_id=${user}&language=${language_id}&set_id=${set_id}`);
              if (!response.ok) {
                  console.error('Failed to fetch flashcards');
                  return;
              }
              const data = await response.json();

              setFlashcards(data.flashcards);
          } catch (error) {
              console.error('Error fetching flashcards:', error);
              setError('Failed to load flashcards');
          } finally {
              setLoading(false);
          }
      };
      fetchFlashcards();
  }, [language_id, set_id, user, token]);

  const handleAddFlashcard = () => {
      navigate(`/add-flashcard/${language_id}/${set_id}`);
  }

  
  const handleDeleteFlashcard = async (flashcard_id) => {
    if (window.confirm('Are you sure you want to delete this flashcard?')) {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/deleteFlashcard?user_id=${localStorage.getItem('user_id')}&language=${language_id}&set_id=${set_id}&flashcard_id=${flashcard_id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            if (!response.ok) {
                console.error('Failed to delete flashcard');
                return;
            }
            const data = await response.json();
            console.log('Flashcard deleted successfully:', data);
            setFlashcards(flashcards.filter(flashcard => flashcard.flashcard_id !== flashcard_id));
        } catch (error) {
            console.error('Error deleting flashcard:', error);
        }
    }
  }

  if (loading) {
    return <div>Loading...</div>;
  }
  if (error) {
      return <div>Error: {error}</div>;
  }

  return (
    <div className="flashcard-container">
      <h1>Flashcards</h1>

      <div className="flashcard-button-group">
        <button onClick={() => navigate(`/set/${language_id}`)}>Back to Sets</button>
        <button onClick={handleAddFlashcard}>Add Flashcard</button>
      </div>

      <div className="flashcard-list">
        {flashcards.length === 0 ? (
          <p>No flashcards available. Please add some.</p>
        ) : (
          flashcards.map(flashcard => (
            <FlashcardCard 
              key={flashcard.flashcard_id} 
              flashcard={flashcard} 
              onDelete={() => handleDeleteFlashcard(flashcard.flashcard_id)}
              language_id={language_id} 
              set_id={set_id}
            />
          ))
        )}
      </div>
    </div>
  );
}
export default Flashcard;


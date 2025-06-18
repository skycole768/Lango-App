import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Home.css';
import LanguageCard from '../components/LanguageCard';

function Home() {
    const navigate = useNavigate();
    const [languages, setLanguages] = useState([]);
    const [error, setError] = useState(null);
    const [user,setUser ] = useState(null);
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
        const fetchLanguages = async () => {
            if (!token) return;
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/getLanguages?user_id=${user}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    console.error('Failed to fetch languages');
                    return;
                }
                const data = await response.json();
                setLanguages(data.languages);
                
            } catch (error) {
                console.error('Error fetching languages:', error);
                setError('Failed to load languages');
            }
        }
        fetchLanguages();
    }
    , [user, token]);
    

    const handleDeleteLanguage = async (language_id) => {
        if (window.confirm('Are you sure you want to delete this Language and all the associated Sets and Flashcards?')) {
            try{
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/deleteLanguage?user_id=${user}&language=${language_id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    console.error('Failed to delete language');
                    return;
                }
                const data = await response.json();
                console.log('Language deleted successfully:', data);
                setLanguages(languages.filter(language => language !== language_id));
            }
            catch (error) {
                console.error('Error deleting language:', error);
            }
        }
    }

    const handleAddLanguage = () => {
        navigate('/add-language');
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div className="home-container">
            <h1>🌱 Welcome to Lango</h1>
            <p className="intro-text">Start building your vocabulary one set at a time.</p> 
            { token && (
                <div className="language-list">
                    <h2>Your Languages</h2>
                    <button onClick={handleAddLanguage}>Add Language</button>
                    {languages.length > 0 ? (
                        languages.map((language) => (
                            <LanguageCard
                                key={language}
                                language={language}
                                onDelete={() => handleDeleteLanguage(language)}
                            />
                        ))
                    ) : (
                        <p>No languages available. Please add some.</p>
                    )}
                </div>
            )}
            {!token && (
                <div className="login-prompt">
                    <p>Please log in or sign up to access your languages.</p>
                    <button onClick={() => navigate('/login')}>Login</button>
                    <button onClick={() => navigate('/signup')}>Sign Up</button>
                </div>
            )}
        </div>
    );
}
export default Home;
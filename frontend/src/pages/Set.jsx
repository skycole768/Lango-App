import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import SetCard from '../components/SetCard';
import '../styles/Set.css';

function Set() {
    const { language_id } = useParams();
    const [sets, setSets] = useState(null);
    const navigate = useNavigate();
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
        const fetchSets = async () => {
            if (!token) return;
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/getSets?user_id=${user}&language=${language_id}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch sets');
                }
                const data = await response.json();
                setSets(data.sets);
            } catch (err) {
                setError(err.message);
            }
        };

        fetchSets();
    }
    , [token, user, language_id]);

    const handleAddSet = () => {
        navigate(`/add-set/${language_id}`);
    };

    const handleDeleteSet = async (set_id) => {
        if (window.confirm('Are you sure you want to delete this set?')) {
            try {
                const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/deleteSet?user_id=${user}&language=${language_id}&set_id=${set_id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                if (!response.ok) {
                    throw new Error('Failed to delete set');
                }
                setSets(sets.filter(set => set.set_id !== set_id));
            } catch (err) {
                setError(err.message);
            }
        }
    };

    if (error) {
        return <div>Error: {error}</div>;
    }
    return (
        <div className="set-container">
            <h1>Sets for {language_id}</h1>
            <div className="set-button-group">
            <button className="cancel-button" onClick={() => navigate('/')}>Back to Home</button>
                <button className="submit-button" onClick={handleAddSet}>Add Set</button>
            </div>
            <div className="set-list">
                {sets && sets.length > 0 ? (
                    sets.map(set =>  (
                        <SetCard
                            key={set.set_id}
                            set={set}
                            language_id={language_id}
                            onDelete={() => handleDeleteSet(set.set_id)}
                        />
                    ))
                ) : (
                    <p>No sets available. Please add some.</p>
                )}
            </div>
        </div>
    );
}
export default Set;
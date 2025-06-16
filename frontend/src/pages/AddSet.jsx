import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/AddSet.css';

function AddSet() {
    const {language_id} = useParams();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [error, setError] = useState(null);

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

        if (!token) return;

        try{
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/addSet?user_id=${user}&language=${language_id}`, {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                'set_name': name,
                'set_description': description,
                }),
            });
        
            if (!response.ok) {
                throw new Error("Failed to add set.");
            }
        
            const data = await response.json();
            console.log('Set added:', data);
            navigate(`/set/${language_id}`);

        } catch (error) {
            console.error('Error adding set:', error);
            setError('Failed to add set. Try again later.');
          }
    }
  
    return (
      <div className="add-set-container">
        <h2>Add New Set</h2>
        <form onSubmit={handleSubmit}>
          <label>
            Set Title:
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
  
          <label>
            Description (optional):
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            ></textarea>
          </label>
  
          <div className="button-group">
            <button
                type="submit"
                className="submit-button"
                disabled={!name}
            >
                Create Set
            </button>
            <button
                type="button"
                className="cancel-button"
                onClick={() => navigate(`/set/${language_id}`)}
            >
                Cancel
            </button>
            </div>
        </form>
        {error && <p className="error-message">{error}</p>}
      </div>
    );
  }
  
  export default AddSet;
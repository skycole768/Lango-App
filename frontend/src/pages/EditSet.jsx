import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/EditSet.css';

function EditSet() {
    const { language_id, set_id } = useParams();
    const navigate = useNavigate();
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
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

    // Fetch existing set info on mount
    useEffect(() => {
    async function fetchSet() {
        if (!token) return;

        try{
            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL}/getSet?user_id=${user}&language=${language_id}&set_id=${set_id}`,
                {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to edit set.");
            }

            const data = await response.json();
            setName(data.set_name || '');
            setDescription(data.set_description || '');
        } catch (error) {
            console.error('Error editing set:', error);
            setError('Failed to edit set. Try again later.');
        }
    }
        fetchSet();
    }, [token, user, language_id, set_id]);

  // Handle update
  async function handleSubmit(e) {
    e.preventDefault();
    if (!token) return;

    try{

        const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/editSet?user_id=${user}&language=${language_id}&set_id=${set_id}`,
        {
            method: 'PUT',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({
            "set_name": name,
            "set_description": description,
            }),
        }
        );

        if (!response.ok) {
            throw new Error('Failed to update set.');
        }

        const data = await response.json();
        console.log('Set updated:', data);
        navigate(`/set/${language_id}`);
    } catch (error) {
        console.error('Error updating set:', error);
        setError('Failed to update set. Try again later.');
    }
  }

  return (
    <div className="edit-set-container">
      <h2>Edit Set</h2>
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
            <button type="submit" className="submit-button" disabled={!name}>Update Set</button>
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

export default EditSet;

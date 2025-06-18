import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Profile.css';

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    password: '',
    preferred_language: ''
  });
  const [error, setError] = useState(null);

  function isValidPassword(password) {
    const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+={}[\]|\\:;"'<>,.?/~`]).{8,}$/;
    return regex.test(password);
  }

  function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  }

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    if (!storedUserId) {
      navigate('/');
      return;
    }

    async function fetchUser() {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/getUser?user_id=${storedUserId}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) throw new Error('Failed to fetch user info');

        const data = await response.json();
        setUser(data);
        setFormData({
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          username: data.username || '',
          password: '',
          preferred_language: data.preferred_language || ''
        });
      } catch (err) {
        console.error(err);
        setError('Could not load user info.');
      }
    }

    fetchUser();
  }, [navigate]);

  async function handleUpdate(e) {
    e.preventDefault();
    setError(null);

    const { first_name, last_name, username, password, preferred_language } = formData;

    if (!first_name || !last_name || !username || !preferred_language) {
      alert('Please fill in all required fields');
      return;
    }

    if (!isValidEmail(username)) {
      alert('Please enter a valid email address');
      return;
    }

    if (password && !isValidPassword(password)) {
      alert('Password must be at least 8 characters long and include an uppercase letter, number, and symbol');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/editUser?user_id=${localStorage.getItem('user_id')}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) throw new Error('Update failed');

      // We no longer need to assign the response JSON since it's unused
      await response.json();

      setUser({
        ...user,
        first_name,
        last_name,
        username,
        preferred_language
      });
      setEditMode(false);
      setFormData({ ...formData, password: '' });

    } catch (err) {
      console.error(err);
      setError('Could not update profile.');
    }
  }

  async function handleDelete() {
    const confirm = window.confirm("Are you sure you want to delete your account? This cannot be undone.");
    if (!confirm) {
      setError(null);
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/deleteUser?user_id=${localStorage.getItem('user_id')}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      });

      if (!response.ok) throw new Error('Delete failed');

      localStorage.clear();
      window.location.reload();
      navigate('/');
    } catch (err) {
      console.error(err);
      setError('Could not delete account.');
    }
  }

  if (!user) return <p>Loading profile...</p>;

  return (
    <div className="profile-container">
      <h2>User Profile</h2>

      {editMode ? (
        <form onSubmit={handleUpdate}>
          <label>
            First Name:
            <input
              type="text"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
              required
            />
          </label>

          <label>
            Last Name:
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
              required
            />
          </label>

          <label>
            Username (email):
            <input
              type="email"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </label>

          <label>
            Preferred Language:
            <select
                value={formData.preferred_language}
                onChange={(e) => setFormData({ ...formData, preferred_language: e.target.value })}
                required
            >
                <option value="English">English</option>
                <option value="Korean">Korean</option>
                <option value="Hindi">Hindi</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="Japanese">Japanese</option>
                <option value="Chinese">Chinese</option>
                <option value="German">German</option>
                <option value="Italian">Italian</option>
                <option value="Portuguese">Portuguese</option>
                <option value="Arabic">Arabic</option>
                <option value="Russian">Russian</option>
            </select>
            </label>

          <label>
            New Password:
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="Leave blank to keep current password"
            />
          </label>

          <button type="submit">Save Changes</button>
          <button
            type="button"
            onClick={() => {
              setEditMode(false);
              setError(null);
            }}
          >
            Cancel
          </button>
        </form>
      ) : (
        <div className="profile-details">
          <p><strong>First Name:</strong> {user.first_name}</p>
          <p><strong>Last Name:</strong> {user.last_name}</p>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Preferred Language:</strong> {user.preferred_language}</p>
          <p><strong>Created At:</strong> {user.created_at}</p>
          <p><strong>Last Login:</strong> {user.last_login}</p>
          <div className="profile-actions">
            <button
              className="profile-button"
              onClick={() => {
                setEditMode(true);
                setError(null);
              }}
            >
              Edit Profile
            </button>
            <button className="profile-button delete" onClick={handleDelete}>
              Delete Account
            </button>
          </div>
        </div>
      )}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default Profile;



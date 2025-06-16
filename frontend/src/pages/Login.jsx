import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Login.css';

function Login(){
    const navigate = useNavigate();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "username": email, "password": password }),
            });

            if (!response.ok) {
                throw new Error('Login failed');
            }

            const data = await response.json();
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('token', data.token);
            navigate('/');
            window.location.reload();
        } catch (err) {
            console.error('Error:', err);
            setError("Invalid username or password.");
        }
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
                {error && <p className="error">{error}</p>}
            </form>
            <p className="signup-link">
                Don't have an account? <span onClick={() => navigate('/signup')}>Sign Up</span>
            </p>
        </div>
    );
}
export default Login;
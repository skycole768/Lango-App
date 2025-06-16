import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Signup.css';

function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

function isValidPassword(password) {
    const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+={}[\]|\\:;"'<>,.?/~`]).{8,}$/;
    return regex.test(password);
}


function Signup() {
    const navigate = useNavigate();
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [preferredLanguage, setPreferredLanguage] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const storedUser = localStorage.getItem('user_id');
        if (storedUser) {
           navigate('/');
        }  
    }, [navigate]);

    const handleSignup = () => {

        if (!firstName || !lastName || !email || !password || !preferredLanguage) {
            alert('Please fill in all fields');
            return;
        }

        if (!isValidEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }
        
        if (!isValidPassword(password)) {
            alert('Password must be at least 8 characters long and include an uppercase letter and a number');
            return;
        }

        const userData = {
            "first_name": firstName,
            "last_name": lastName,
            "username": email,
            "password": password,
            "preferred_language": preferredLanguage
        };

        fetch(`${import.meta.env.VITE_API_BASE_URL}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        })
        .then(response => {
            if (!response.ok) {
              return response.json().then(err => {
                // Throw detailed error from server if available
                throw new Error(err.error || 'Signup failed.');
              });
            }
            return response.json();
          })
        .then(data => {
            localStorage.setItem('user_id', data.user_id);
            localStorage.setItem('token', data.token);
            navigate('/');
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            setError(error.message);
        });
    };

    return (
        <div className="signup-container">
            <h2>Sign Up</h2>
            <input
                type="text"
                placeholder="First Name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
            />
            <input
                type="text"
                placeholder="Last Name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
            />
            <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
             <select
            value={preferredLanguage}
            onChange={(e) => setPreferredLanguage(e.target.value)}
            >
                <option value="" disabled>-- Select Preferred Language --</option>
                <option value="English">English</option>
                <option value="Hindi">Hindi</option>
                <option value="Portuguese">Portuguese</option>
                <option value="Korean">Korean</option>
                <option value="Japanese">Japanese</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
                <option value="Chinese">Chinese</option>
                <option value="Arabic">Arabic</option>
                <option value="Russian">Russian</option>
                <option value="Italian">Italian</option>
            </select>
            {error && <p className="error">{error}</p>}
            <button onClick={handleSignup}>Sign Up</button>
            <p className="login-link">
                Already have an account? <span onClick={() => navigate('/login')}>Login</span>
            </p>
        </div>
    );
}
export default Signup;
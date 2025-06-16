import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/NavBar.css';

function NavBar() {
    const navigate = useNavigate();
    const [token, setToken] = useState(null);
    const [user, setUser] = useState(null);
    const [userName, setUserName] = useState(null);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        const storedUserId = localStorage.getItem('user_id');
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setUser(storedUserId);
            setToken(storedToken);
            fetchUser(storedUserId);
        }  
    }, []);

    async function fetchUser(user_id) {
        try {
            const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/getUser?user_id=${user_id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            console.log("Response status:", response.status);

            if (!response.ok) {
                throw new Error(`Failed to fetch user_id: ${user_id} (status: ${response.status})`);
            }

            const data = await response.json();
            setUserName(data.first_name || 'User');
        } catch (error) {
            console.error('Error fetching user:', error);
        }
    }

    const handleLogout = () => {
        localStorage.removeItem('user_id');
        localStorage.removeItem('token');
        setUser(null);
        setUserName(null);
        navigate('/');
        window.location.reload();
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand" onClick={() => navigate('/')}>
                Lango
            </div>

            <div className="navbar-hamburger" onClick={() => setMenuOpen(prev => !prev)}>
                ☰
            </div>

            <div className={`navbar-links ${menuOpen ? 'active' : ''}`}> {/* ✅ */}
                {token && userName ? (
                    <>
                        <span className="navbar-user-clickable" onClick={() => navigate('/profile')}>
                            Welcome {userName}
                        </span>
                        <button className="navbar-logout" onClick={handleLogout}>
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <button className="navbar-login" onClick={() => navigate('/login')}>Login</button>
                        <button className="navbar-signup" onClick={() => navigate('/signup')}>Sign Up</button>
                    </>
                )}
            </div>
        </nav>
    );
}

export default NavBar;
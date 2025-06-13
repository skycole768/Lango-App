import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/NavBar.css';

function NavBar() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }  
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('user');
        setUser(null);
        navigate('/');
    };

    return (
        <nav className="navbar">
            <div className="navbar-brand" onClick={() => navigate('/')}>
                Lango
            </div>
            <div className="navbar-links">
                {user ? (
                    <>
                        <span className="navbar-user">Welcome, {user.name}</span>
                        <button className="navbar-logout" onClick={handleLogout}>Logout</button>
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
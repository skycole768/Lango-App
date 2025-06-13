import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Home.css';

function Home() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        }  
    }, [navigate]);

    return (
        <div className="home-container">
            <h1>Welcome to Lango</h1>
            <p>Your language learning journey starts here.</p>
            {user ? (
                <h1 > Language </h1>
            ):(
                <h1> Sign Up Today </h1>
        )}
            
        </div>
    );
}
export default Home;
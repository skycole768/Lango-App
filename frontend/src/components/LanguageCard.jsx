import { useNavigate } from 'react-router-dom';
import React from 'react';
import '../styles/LanguageCard.css';

function LanguageCard({ language, onDelete }) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/set/${language}`);
  };

  return (
    <div className="language-card" onClick={handleClick}>
      <div className="language-content">
        <h1>{language}</h1>
        <button
          className="delete-button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default LanguageCard;

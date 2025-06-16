import { useNavigate } from 'react-router-dom';
import React from 'react';
import '../styles/SetCard.css';

function SetCard({ set, onDelete, language_id}) {
    const navigate = useNavigate();

    const handleClick = () => {
        navigate(`/flashcard/${language_id}/${set.set_id}`);
    };

    return (
        <div className="set-card" onClick={handleClick}>
            <h3>{set.set_name}</h3>
            <p className="description">{set.set_description}</p>

            <div className="button-container">
                <button
                onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/edit-set/${language_id}/${set.set_id}`);
                }}
                >
                Edit
                </button>
                <button
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
export default SetCard;

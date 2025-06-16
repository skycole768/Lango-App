
import React, { useState } from 'react';
import { useNavigate} from 'react-router-dom';
import '../styles/FlashcardCard.css';

function FlashcardCard({flashcard, onDelete, language_id, set_id}) {
    const [flipped, setFlipped] = useState(false);

    const toggleFlip = () => {
        setFlipped(!flipped);
    }

    const navigate = useNavigate();
       
    return  (
      <div className="flashcard-wrapper">
        <div
          className={`flashcard ${flipped ? 'flipped' : ''}`}
          onClick={toggleFlip}
        >
          <div className="flashcard-front">
            <h1>{flashcard.word}</h1>
            <h3>{flashcard.usage}</h3>
          </div>
          <div className="flashcard-back">
            <h1>{flashcard.translated_word}</h1>
            <h3>{flashcard.translated_usage}</h3>
          </div>
        </div>
  
        <div className="flashcard-action-buttons">
          <button
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/edit-flashcard/${language_id}/${set_id}/${flashcard.flashcard_id}`);
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
  
  export default FlashcardCard;
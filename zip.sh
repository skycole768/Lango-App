#!/bin/bash

# Define all your Lambda function names
functions=(
  add_flashcard edit_flashcard delete_flashcard get_flashcards get_flashcard
  add_set edit_set delete_set get_sets get_set
  add_language delete_language get_languages get_language
  add_user delete_user edit_profile get_profile
  signup login
)

# Navigate to the lambdas directory (adjust if needed)
cd lambdas || { echo "lambdas directory not found"; exit 1; }

# Loop through each function and zip it
for func in "${functions[@]}"; do
  if [ -f "${func}.py" ]; then
    zip -j "${func}.zip" "${func}.py"
    echo "Zipped ${func}.py into ${func}.zip"
  else
    echo "⚠️  Warning: ${func}.py not found, skipping."
  fi
done

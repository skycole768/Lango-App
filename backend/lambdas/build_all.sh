#!/bin/bash

# Directories to process
dirs=(auth set user language flashcard)

# Output zip directory inside lambdas/
output_dir="zip"

mkdir -p "$output_dir"

for dir in "${dirs[@]}"; do
  echo "Processing $dir ..."

  lambda_dir="$dir"
  package_dir="$lambda_dir/package"

  # Clean previous package folder if exists
  rm -rf "$package_dir"
  mkdir -p "$package_dir"

  # Install dependencies if requirements.txt exists
  if [ -f "$lambda_dir/requirements.txt" ]; then
    echo "Installing dependencies for $dir ..."
    pip install -r "$lambda_dir/requirements.txt" -t "$package_dir"
  else
    echo "No requirements.txt found for $dir, skipping pip install"
  fi

  # Copy all .py files from lambda directory to package/
  cp "$lambda_dir"/*.py "$package_dir"/

  # Zip the contents of package/
  (
    cd "$package_dir" || exit
    zip -r "../../$output_dir/$dir.zip" .
  )

  # Clean up package directory
  rm -rf "$package_dir"

  echo "$dir.zip created in $output_dir/"
done

echo "All done!"




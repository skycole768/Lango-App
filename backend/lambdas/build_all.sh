#!/bin/bash

# Lambda directories to process
dirs=(flashcard)

# Output directory for zip files
output_dir="zip"

mkdir -p "$output_dir"

# Install dependencies once (optional)
yum install -y python39 python3-pip zip gcc

for dir in "${dirs[@]}"; do
  echo "Processing $dir ..."

  lambda_dir=$dir
  package_dir=$lambda_dir/package

  rm -rf "$package_dir"
  mkdir -p "$package_dir"

  if [ -f "$lambda_dir/requirements.txt" ]; then
    echo "Installing dependencies for $dir ..."
    pip3 install -r "$lambda_dir/requirements.txt" -t "$package_dir"
  else
    echo "No requirements.txt found for $dir, skipping pip install"
  fi

  cp "$lambda_dir"/*.py "$package_dir"/

  (cd "$package_dir" && zip -r "../../$output_dir/$dir.zip" .)

  rm -rf "$package_dir"

  echo "$dir.zip created in $output_dir/"
done

echo "All done!"







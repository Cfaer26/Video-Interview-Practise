#!/bin/bash
# Check for Homebrew
if ! command -v brew &> /dev/null; then
  echo "Please install Homebrew first: https://brew.sh/"
  exit 1
fi

# Install python3 and ffmpeg if missing
brew install python ffmpeg

# Create venv if not present
[ -d venv ] || python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run the app
export FLASK_APP=app.py
python app.py
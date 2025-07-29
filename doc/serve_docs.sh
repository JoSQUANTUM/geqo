PORT=${1:-8301}

echo "Building the Jupyter Book..."
jupyter-book build .

if [ $? -ne 0 ]; then
  echo "Build failed. Exiting."
  exit 1
fi

echo "Serving the site at http://0.0.0.0:$PORT"
cd _build/html
python3 -m http.server "$PORT" --bind 0.0.0.0
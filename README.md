# Homer
Local home server

### Prerequisites
- Linux
- Python 3.13

### To run
- install UV `pipx install uv`
- install Python dependencies `uv sync`
- `source .venv/bin/activate`
- run the app `make run-dev`
- OR `gunicorn -b localhost:8000 -w 2 garden:app` when run on server

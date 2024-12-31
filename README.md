# Homer
Local home server

### Prerequisites
- Linux
- Python 3.13

### To run locally
- install UV `pipx install uv`
- install Python dependencies `uv sync` (this will create the `.venv`)
- run the app in debug mode `make run-dev`
- OR run production-like with `make run-prod`

### To run on server
- install system deps `sudo apt install supervisor nginx`
- add `.env` file with required configs (SECRET_KEY, ...)
- create config `/etc/supervisor/conf.d/homer.conf`
```ini
[program:homer]
command=/path/to/.venv/bin/gunicorn -b localhost:8000 -w 2 homer:app
directory=/path/to/homer
user=server-user
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```
- reload config `sudo supervisorctl reload`
- [configure nginx](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) if needed (different port than 80)

### Add users
App will run on local network only. For now users are added manually like this:
- activate virtual environment (server or dev)
```python
>>> from garden import app
>>> from homer import db
>>> from homer.models import User
>>> app.app_context().push() # to work in app context
>>> u = User(username="Foo")
>>> u.set_password("secret")
>>> db.session.add(u)
>>> db.session.commit()
```

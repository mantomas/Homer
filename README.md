# Homer
Local home server

### Prerequisites
- Linux
- Python 3.13

### To run locally
- install UV `pipx install uv`
- install Python dependencies `uv sync` (this will create the `.venv` with all deps including dev)
- run the app in debug mode `make run-dev`
- OR run production-like with `make run-prod`

### To run on server
- install system deps `sudo apt install supervisor nginx pipx`
- install `uv` to manage Python dependencies
- clone the project and `cd` into it
- add `.env` file with required configs
    - SECRET_KEY
    - DATABASE_URL in form of `sqlite:////home/user/path/to/db/db.sqlite3`. It must be an absolute path after removing the `sqlite:///` prefix.
- init the `.venv` by running `uv sync --no-dev`
- create config `/etc/supervisor/conf.d/homer.conf`
```ini
[program:homer]
command=/path/to/Homer/.venv/bin/gunicorn -b localhost:8000 -w 2 homer:app
directory=/path/to/homer
user=server-user
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```
- reload config `sudo supervisorctl reload`
- [configure nginx](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) if needed (different port than 80)

### Server upgrade
- ssh to the server
- go to the Homer root
- run the upgrade script `./upgrade.sh`
    - script calls `sudo` for some commands internaly which is not ideal, but is the least pain fix all non-sudo commands to be executed as a regular user
- DB backup will be stored in `./backups`

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

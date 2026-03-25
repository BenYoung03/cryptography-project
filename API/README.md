# API Documentation
## Running Docker
Docker deployment will be as simple as cloning the repo and running compose!!

First install docker: https://docs.docker.com/engine/install/
Or the windows install: https://docs.docker.com/desktop/setup/install/windows-install/; need to use powershell or just the GUI (i have never used it)

If you dont want to be running sudo all the time you can follow the post install instructions to set it up differently, also see windows commands in the docs if you are on a windows machine (should be the same w/out the sudo).

FIRST MAKE SURE YOU ARE IN THE DIRECTORY WITH THE COMPOSE FILES

ALSO MAKE SURE YOU HAVE A FIREBASE SERVICE FILE!!

Compose runs and handles all the volumes, networks and services!!
```bash
docker compose up --build
```

For the server you run:
```bash
docker compose --env-file .env.server -f compose.yaml -f compose.server.yaml up --build
```

Then just go to http://localhost/docs to see the api!!

For the frontend it should auto fallback to localhost if cyllenian.jolyne.org is not up!!

**NOTE**: Make sure nothing is occupying your localhost:80!!! if so please stop them from running to run this app; or run
```bash
docker compose -f compose.notraefik.yaml up --build
```
Do note the frontend would not be able to handle this; in that case please go in and change from localhost to localhost:8000 yourself; or just disable whatevers listening on HTTP/port 80 on your machine please!!

### Shutting Down
Simply Ctrl+C out of the context and run
```bash
docker compose down
```


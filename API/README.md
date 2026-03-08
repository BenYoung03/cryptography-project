# API Documentation
Make sure your using a python 3.12.12 virtual environment for development and installing its packages from the requirements (none so far)

This document will be used to run through setting up a dev environment (doing my best!! ask me if you run into issues) - Jolyne

## Poetry Setup and Management
Please not this is only if you want to develop and probably can skip the whole version thingy. The services environment is handled in its docker file

Make sure you install poetry: https://python-poetry.org/docs/
you can install python 3.12.12 with:
```bash
poetry python install 3.12.12
poetry env use 3.12.12
```

Run to activate environment:
```bash
source "$(poetry env info --path)/bin/activate"
```
**NOTE**: Not at all nessecary for development, the app will not work outside of the docker environment as we rely on redis and dockers routing to access it.

Install dependencies:
```bash
poetry install
```

If you want to edit the dependencies make sure to run:
```bash
poetry add <package-name>
poetry export -f requirements.txt --without-hashes -o requirements.txt
```

## Docker Documentation
Docker deployment will be as simple as cloning the repo and running compose!!

First install docker: https://docs.docker.com/engine/install/

If you dont want to be running sudo all the time you can follow the post install instructions to set it up differently, also see windows commands in the docs if you are on a windows machine (should be the same w/out the sudo).

Compose runs and handles all the volumes, networks and services!! usually just used the compose inside the working directory when ran, but for dev we have another compose that just enables live code updates (mounts src as a volume!!), and runs the reload command on uvicorn.
```bash
sudo docker compose -f compose.yaml -f compose.dev.yaml up
```

Then just go to http://localhost:8000/docs to see the api!! Server will be setup to handle routing with Nginx and https.

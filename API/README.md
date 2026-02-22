# API Documentation
Make sure your using a python 3.12.12 virtual environment for development and installing its packages from the requirements (none so far)

This document will be used to run through setting up a dev environment (doing my best!! ask me if you run into issues) - Jolyne

## Poetry Setup and Management
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
For deployment to a server I will write up a bash script and put it on the server!! should just run that. This section will be for running the docker in a dev environment (api code, especially the SQLite is written with the assumption of a docker environment as defined, likely won't work when run directly).

First install docker: https://docs.docker.com/engine/install/

If you dont want to be running sudo all the time you can follow the post install instructions to set it up differently, also see windows commands in the docs if you are on a windows machine (should be the same w/out the sudo).

Build the docker file, make sure you have the repo and are in /API (server script will build the docker directly from the repo) and run:
```bash
sudo docker build -t api:latest .
```

It will run the build script (should take a minute or two), once its complete run (can expose any port, using 8000 for simplicity):
```bash
sudo docker run -d \
  -p 8000:8000 api:latest \
  -v <mount-path>/api-data:/data \
  --name api-mount \
  api:latest
```

This command uses a mount (plugs into a folder on your machine), this is so you can see and edit the db for testing. The server will utilize a docker volume which is more opaque and managed by docker. this is done for increased security. It looks all the same inside the docker instance.

Then just go to http://localhost:8000/docs to see the api!! Server will be setup to handle routing with Nginx and https.

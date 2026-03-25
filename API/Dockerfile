## Tentative Docker file!! build instructions should be in readme

## Specifies the OS image, this is a debian image (lacking many packages except ones needed for python)
## using 3.12.12 as it is stable and well-supported!!
## This is the "builder" stage, which installs our dependencies; only re-run if dependencies change!!
FROM python:3.12-slim as builder

## sets the working directory for the dockerfile to the API src
WORKDIR /API

## Installs poetry and installs requirements from the poetry.lock and .toml
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./

## Install only main dependencies
RUN poetry install --no-interaction --no-ansi --no-root --only main

## RUNTIME stage
FROM python:3.12-slim

WORKDIR /API

## copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin

## copies the actual source code
COPY src ./src

## opens port (must pass the docker this port!!)
EXPOSE 8000

## Runs the API app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

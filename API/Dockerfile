    ## Tentative Docker file!! build instructions should be in readme

    ## Specifies the OS image, this is a slimmed down debian image (lacking many packages except ones needed for python)
    ## using 3.12.12 as it is stable and well-supported!!
    FROM python:3.12.12

    ## sets the working directory for the dockerfile to the API src
    WORKDIR /API

    ## copies and runs requirements.txt
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    ## copies the actual source code
    COPY src ./src

    ## opens port (must pass the docker this port!!)
    EXPOSE 8000

    ## Runs the API app
    CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

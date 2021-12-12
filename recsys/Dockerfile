FROM python:3.9


RUN pip install --no-cache-dir --upgrade fastapi==0.68.0 pydantic==1.8.2 \
    uvicorn==0.15.0 requests myloginpath mysqlclient fastapi-utils beautifulsoup4

RUN apt update -y && apt-get install build-essential

RUN pip install n2

WORKDIR /project
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

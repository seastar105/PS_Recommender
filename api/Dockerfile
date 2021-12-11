<<<<<<< Updated upstream
FROM python:3.9

RUN pip install --no-cache-dir --upgrade fastapi==0.68.0 pydantic==1.8.2 \
    uvicorn==0.15.0 requests myloginpath mysqlclient fastapi-utils
=======
FROM python:3.9

RUN pip install --no-cache-dir --upgrade fastapi==0.68.0 pydantic==1.8.2 \
    uvicorn==0.15.0 requests myloginpath mysqlclient fastapi-utils

WORKDIR /api/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
>>>>>>> Stashed changes

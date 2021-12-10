docker stop test_api
docker run -itd --rm --name test_api -p 8000:80 -v $(pwd):/api fastapi bash

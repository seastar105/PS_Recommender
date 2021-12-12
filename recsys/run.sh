docker stop prod_api
docker run -d --rm --name prod_api -p 8000:80 -v $(pwd):/project recsys_prod

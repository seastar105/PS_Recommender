docker stop web_server
docker run --rm -d -v $(pwd):/app -p 80:8080 --name web_server webapp
docker stop web_server
docker run -d -v $(pwd):/app -p 80:8080 webapp
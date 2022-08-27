docker build -t your-docker-hub-id/imbroker-feishu-receiver .
docker push your-docker-hub-id/imbroker-feishu-receiver
docker run --env-file .env -p 8080:8080 -it your-docker-hub-id/imbroker-feishu-receiver

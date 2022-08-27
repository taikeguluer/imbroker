docker build -t your-docker-hub-id/imbroker-wxwork-robot-sender .
docker push your-docker-hub-id/imbroker-wxwork-robot-sender
docker run -p 8080:8080 -it your-docker-hub-id/imbroker-wxwork-robot-sender

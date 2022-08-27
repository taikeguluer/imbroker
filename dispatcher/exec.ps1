docker build -t your-docker-hub-id/imbroker-dispatcher .
docker push your-docker-hub-id/imbroker-dispatcher
docker run -p 8080:8080 -it your-docker-hub-id/imbroker-dispatcher

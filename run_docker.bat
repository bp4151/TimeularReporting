docker build . -t timeular_reporting --force-rm
docker run --rm --env-file .env timeular_reporting
docker rmi --force timeular_reporting:latest
pause
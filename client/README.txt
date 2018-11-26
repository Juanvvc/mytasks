docker build -t jvera/mytasks .
docker run -it -p 8080:80 --rm --name mytasks-1 jvera/mytasks

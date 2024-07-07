heroku login
heroku container:login
heroku create getaroundapi
docker build . -t getaroundapi --platform linux/amd64
docker tag getaroundapi registry.heroku.com/getaroundapi/web
docker push registry.heroku.com/getaroundapi/web
heroku container:release web -a getaroundapi
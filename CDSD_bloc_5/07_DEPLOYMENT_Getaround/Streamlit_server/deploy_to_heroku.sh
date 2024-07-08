heroku login
heroku container:login
heroku create getaround01
docker build . -t getaround01 --platform linux/amd64
docker tag getaround01 registry.heroku.com/getaround01/web
docker push registry.heroku.com/getaround01/web
heroku container:release web -a getaround01
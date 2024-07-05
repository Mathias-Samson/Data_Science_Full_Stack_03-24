heroku login
heroku container:login
heroku create walletscan-app
docker build . -t getaround_01 --platform linux/amd64
docker tag walletscan-app registry.heroku.com/walletscan-app/web
docker push registry.heroku.com/getaround_01/web
heroku container:release web -a getaround_01
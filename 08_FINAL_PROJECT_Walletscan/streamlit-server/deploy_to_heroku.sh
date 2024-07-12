heroku login
heroku container:login
heroku create walletscan-app
docker build . -t walletscan-app --platform linux/amd64
docker tag walletscan-app registry.heroku.com/walletscan-app/web
docker push registry.heroku.com/walletscan-app/web
heroku container:release web -a walletscan-app
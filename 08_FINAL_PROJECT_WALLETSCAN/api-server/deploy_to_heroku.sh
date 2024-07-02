heroku login
heroku container:login
#heroku create walletscan-api
docker build . -t walletscan-api --platform linux/amd64
docker tag walletscan-api registry.heroku.com/walletscan-api/web
docker push registry.heroku.com/walletscan-api/web
# FORMAT WARNING >> The default credentials.json format doesn't work for Heroku...requires `//n`rather than `/n`
#heroku config:set -a walletscan-api GOOGLE_JSON_CREDENTIALS="$(< env/heroku-gcp-credentials.json)"
#heroku config:set -a walletscan-api GOOGLE_APPLICATION_CREDENTIALS=gcp-credentials.json
#heroku config:set -a walletscan-api GOOGLE_CLOUD_PROJECT=eth-blockchain-425408
heroku container:release web -a walletscan-api
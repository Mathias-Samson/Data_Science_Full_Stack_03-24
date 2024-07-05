heroku login
heroku container:login
heroku create getaround_api_01
docker build . -t getaround_api_01 --platform linux/amd64
docker tag getaround_api_01 registry.heroku.com/getaround_api_01/web
docker push registry.heroku.com/getaround_api_01/web
heroku container:release web -a getaround_api_01
# docker run -it -v "$(pwd):/home/app" -p 4000:4000 -e PORT=4000 getaroundapi
docker run -it \
-v "$(pwd):/home/app" \
-p 4000:4000 \
-e PORT=4000 \
getaroundapi # Docker image name


#docker build . -t walletscan-api --platform linux/amd64
export GOOGLE_CLOUD_PROJECT=eth-blockchain-425408
export GOOGLE_APPLICATION_CREDENTIALS=env/gcp-credentials.json # PATH to your Google Cloud credentials.json file
docker run -it \
-v "$(pwd):/home/app" \
-p 4000:4000 \
-e PORT=4000 \
-e GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
walletscan-api # Docker image name


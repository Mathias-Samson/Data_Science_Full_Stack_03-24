#docker build . -t streamlit-app --platform linux/amd64
docker run -it \
    -v "$(pwd):/home/app"\
    -e PORT=80 \
    -e NIXTLA_API_KEY=$NIXTLA_API_KEY \
    -p 4001:80 \
    7cd21adf15cf4a8db8912319df79bb53f650dff6cc29fc9a64b16cee53166bc3
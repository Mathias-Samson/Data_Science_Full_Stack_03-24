#docker build . -t streamlit-app --platform linux/amd64
docker run -it \
    -v "$(pwd):/home/app"\
    -e PORT=80 \
    -p 4001:80 \
    getaround_01
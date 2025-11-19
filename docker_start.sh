HOST_DIR=$(pwd)
docker run -d --name my-runner \
-v ${HOST_DIR}/log:/app/log \
-v ${HOST_DIR}/history:/app/history \
-v ${HOST_DIR}/session:/app/session \
-v /etc/localtime:/etc/localtime:ro \
my-source-image
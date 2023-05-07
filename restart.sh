docker build -t zkp/signature .
docker container stop zkp-signature 
docker container rm zkp-signature
docker container run --name zkp-signature -d zkp/signature
docker logs zkp-signature -f
name="zkp15"
echo $name

docker container stop $name 
docker container rm $name
docker build -t $name .
docker container run --name $name -d $name
docker logs $name -f
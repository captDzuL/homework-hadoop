<<<<<<< HEAD
<<<<<<< HEAD
## No.2

To run it :
1. build the postgres image
```
docker build -t {postgres_image_name} -f Dockerfile.postgres .
```
2. run postgres container
if you want to check the result on local (uncomment first the EXPOSE command on dockerfile postgres)
```
docker run -d -p 5432:5432 --name {postgres_container_name} {postgres_image_name}
```
or if you don't
```
docker run -d --name {postgres_container_name} {postgres_image_name}
```
3. build api image
```
docker build -t {api_image_name} -f Dockerfile.api .
```
4. run api container and link it with postgres container
```
docker run -d -p 8000:8000 --name {api_container_name} --link {postgres_container_}:postgres {api_image_name}
```
5. Open postman or another testing api and run trigger_pokemon_effects_to_csv
```
localhost:8000/trigger_pokemon_effects_to_csv/
```
6. you can look the csv file on /tmp/

# How to Save data with format .csv into hdfs on Hadoop Container?
1. First, you can build and run a hadoop container
```
docker-compose -f docker-hadoop/docker-compose-hadoop.yml up -d
```

2. Then, you can make directory hdfs
```
docker exec docker-hadoop-namenode-1 \
bash -c \
"hadoop fs -mkdir /data-poke"
```

3. And last, you can paste all data that from local system `/scripts/data/*.csv` to hdfs
```
docker exec docker-hadoop-namenode-1 \
bash -c \
"hadoop fs -put /scripts/data/*.csv /data-poke"
```

4. And you can check data in hdfs
```
docker exec docker-hadoop-namenode-1 \
bash -c \
"hadoop fs -ls /data-poke"
```

5. If you want to delete all data in hdfs
```
docker exec docker-hadoop-namenode-1 \
bash -c \
"hadoop fs -rm -f -r /data-poke"
=======
>>>>>>> 3c18b4a (Initial commit)
=======
Brief:

1.	Running hadoop on your local machine using hadoop
2.	Create a python script that hit "https://pokeapi.co/api/v2/ability/" + pokemon_ability_id  from ability id 1 - 999
3.	Save that ability id into csv per 100 ability id (example : id 1 - 100 on result_1_100.csv, id 101 - 200 on result_101_200.csv and so on) with these columns id,pokemon_ability_id,effect,language,short_effect (expected like below picture but with id on the left side of pokemon_ability_id) basically the parsing side is already handled by code that I give on last session.
 
4.	Save the csv into hdfs
5.	Send the result with the code, explain the code, and screenshot of file above on hdfs and zip it all.
6.	Good luck ;)
>>>>>>> 9974b1b (Update README.md)

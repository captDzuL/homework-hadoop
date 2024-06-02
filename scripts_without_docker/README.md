# How is work ?
1. First, you can `venv` for hint API then install requirements
```
# for Windows
python3 -m venv venv
# or
python -m venv venv

# for Linux
source venv/bin/activate
```

2. Then, you can install requirements
```
pip install -r scripts/requirements/modules.txt
```

3. And finally, you can run `python parsing-api.py` on PowerShell or Linux

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
```
docker run \
-p 3306:3306 \
--restart=always \
--name mysql \
--privileged=true \
-v /c:/sandbox/docker-mount/mysql8:/var/log/mysql \
-v /c:/sandbox/docker-mount/mysql8:/var/lib/mysql \
-v /c:/sandbox/docker-mount/mysql8/my.cnf:/etc/mysql/my.cnf \
-e MYSQL_ROOT_PASSWORD=mysql \
-d mysql:8.3.0  


/sandbox/docker-mount/mysql8


docker run \
--restart=always \
--log-opt max-size=100m \
--log-opt max-file=2 \
-p 6379:6379 \
--name redis \
-v //c/sandbox/docker-mount/redis/conf/redis.conf:/etc/redis/redis.conf  \
-v //c/sandbox/docker-mount/redis/data:/data \
-d redis redis-server 
--appendonly yes \
--requirepass 123456 

## Clickhouse docker setup in local (gitbash)
```gitbash
docker run -d -p 8123:8123 -p 9000:9000 --name clickhouse-server --ulimit nofile=262144:262144 \
-e CLICKHOUSE_USER=admin \
-e CLICKHOUSE_PASSWORD=admin \
-u 101:101 \
-v //c/sandbox/docker-mount/clickhouse/data:/var/lib/clickhouse \
-v //c/sandbox/docker-mount/clickhouse/logs:/var/log/clickhouse-server \
clickhouse/clickhouse-server


docker run -d -p 8123:8123 -p 9000:9000 --name clickhouse-server --ulimit nofile=262144:262144 \
-e CLICKHOUSE_USER=admin \
-e CLICKHOUSE_PASSWORD=admin \
clickhouse/clickhouse-server
```
### add clickhouse config
```
-v //c/sandbox/docker-mount/clickhouse/configs/config.xml:/etc/clickhouse-server/config.xml \
```

### connect to clickhouse with docker
```
docker exec -it clickhouse-server clickhouse-client --user admin --password admin
```

git bash 命令：

docker run -d \
  -v //d/docker_data/nginx:/usr/share/nginx/html \
  -p 8087:80 \
  nginx:latest
  
 /d/docker_data/nginx 里面的文件没有挂在生成了一个目录
 /d/docker_data/nginx;C
 
 
 docker run -p 9030:9030 -p 8030:8030 -p 8040:8040 -itd --name quickstart starrocks/allin1-ubuntu
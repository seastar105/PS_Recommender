# start jupyter notebook server
docker run -itd -p 8888:8888 -p 2222:22 -v $(pwd)/recsys:/opt/notebooks --name jupyter_server seastar105/buffalo_jupyter jupyter notebook

# start mysql server
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v /mnt/mysql:/var/lib/mysql --name mysql_server mysql:5.6 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
docker cp .mylogin.cnf jupyter_server:/root/

# start api server
bash recsys/run.sh

# start web server
bash site/run.sh
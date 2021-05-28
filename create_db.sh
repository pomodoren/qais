# create tables into the postgres database
echo "======= BUILDING DATABASE ======="
docker-compose exec api-interview python manage.py db init
docker-compose exec api-interview python manage.py db stamp head
docker-compose exec api-interview python manage.py db migrate
docker-compose exec api-interview python manage.py db upgrade 

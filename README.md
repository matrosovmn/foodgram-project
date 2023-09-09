# Foodgram «Продуктовый помощник» 
сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек технологий использованный в проекте:
- Python 3.x
- backend: Django
- frontend: React
- Django REST Framework
- PostgreSQL
- Nginx
- Gunicorn
- Docker
- Djoser

## Установка на удаленный сервер

Подключаемся к серверу:
```
ssh <имя_сервера>@<публичный_ip_сервера>
```
Устанавливаем docker и docker-compose:
* Установка docker:
```
 sudo apt update
 sudo apt install curl
 curl -fSL https://get.docker.com -o get-docker.sh
```
* Установка docker-compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
Настраиваем внешний nginx (пример):
```
server {
    server_name -your IP address;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:8000;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/zelema.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/zelema.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = -your IP address) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name -your IP address;
    return 404; # managed by Certbot
}
```
Клонируем проект:
```
git@github.com:matrosovmn/foodgram-project-react.git
```
Создаём файл .env (пример):
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django

DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_key_for_django-insecure-

DEBUG=False

ALLOWED_HOSTS=your_domain
```
Находясь в папке infra запускаем docker-compose.production.yml:
```
sudo docker compose -f docker-compose.production.yml up -d
```
Выполняем миграции:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations users
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations recipes
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
Активируем статику админки:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
Создаем суперпользователя (админа):
```
sudo docker exec -it foodgram_backend python manage.py createsuperuser
```
Находясь в папке backend загружаем заготовленный список ингредиентов с единицами измерения и теги в базу данных:
```
python manage.py load_data
python manage.py load_tags
```

В проекте реализована автоматизация деплоя через CD/CI <br>
Проект доступен по адресу https://zelema.ru

Superuser <br>
Логин: AdminYa  
Email: admin@example.com  
Пароль: 123_Patrik  


## Автор
Михаил Матросов - [GitHub](https://github.com/matrosovmn)


# praktikum_new_diplom

server {
    server_name zelema.ru;

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
    if ($host = zelema.ru) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    listen 80;
    server_name zelema.ru;
    return 404; # managed by Certbot
}




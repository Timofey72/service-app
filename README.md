# Django Service App

### Запуск проекта

Проект запускается при помощи докера. Сначала необходимо переименовать файл `.env.example` в  `.env` и поменять переменные по необходимости.

```
docker-compose build
docker-compose up
```

Для применения миграций:
```
docker-compose run --rm web-app sh -c "python manage.py migrate"
```

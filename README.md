## FoodGram - Продуктовый помощник
https://github.com/sayyyeah/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg
### Описание:
В FoodGram участники могут создавать свои кулинарные секреты, следить за новинками в меню других авторов, сохранять полюбившиеся блюда в специальной подборке и, конечно, составлять список нужных ингредиентов для создания одного или нескольких избранных блюд.
Развернутый проект доступен по ссылке: https://sayyyeahfoodgram.ddns.net/recipes

### Как запустить проект:
1. Склонировать репозиторий в командной строке:
```bash
https://github.com/sayyyeah/foodgram-project-react.git
```
Затем перейдите в корневую директорию проекта:
```bash
cd  foodgram-project-react/
```
2. В директории infra/ необходимо создать файл .env, и заполните его по примеру:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<ваш_пароль>
DB_HOST=foodgram_db
DB_PORT=5432
SECRET_KEY=<секретный_ключ_проекта>
```
3. 
В директории infra/ необходимо запустить docker-compose, используя команду:

```bash
docker compose  up  -d
```
4. Создайть миграции командой:
```bash
docker-compose  exec  web  python  manage.py  migrate
```
5. Подгрузить статику:
```bash
docker-compose  exec  web  python  manage.py  collectstatic  --no-input
```
6. При необходимости создайте суперпользователя:
```bash
docker-compose  exec  web  python  manage.py  createsuperuser
```
7. Залейте базовые фикстуры:
```bash
docker-compose  exec  web  python  manage.py  load_tags
docker-compose  exec  web  python  manage.py  load_ingredients
```

### Автор:
Довгалюк Егор

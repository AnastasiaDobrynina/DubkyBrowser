# Dubky Browser
Веб-приложение с возможностью информационного поиска по перепискам чата [Студенческий городок Дубки](https://web.telegram.org/a/#-1001278030013)
***
## Инфопоиск
* Корпус тектов - небольшой кусочек переписок из беседы Дубков. Лежит [тут](https://drive.google.com/drive/u/0/folders/1wynFYtGfYjptvbpO3sg0RQvO4MUJbZiw)
* Два вида индексации: Word2Vec  и TF-IDF
* Предобработка с помощью Seanza: удаление стоп-слов и пунктуации, для TF-IDF просто леммы, для W2V леммы в формате *лемма_POS*. Код предобработки представлен в [тетрадке](https://github.com/hse-courses-tokubetsu/project-AnastasiaDobrynina/blob/main/infopoisk%20research.ipynb). Поступающие запросы обрабатываются аналогичной функцией.
* Поиск осуществляется на уровне запроса к БД с помощью функции. Подсчитывается косинусная близость на основе индекса и заранее посчитанной нормы
* При выдаче результатов выводится время и близость тектов
### API
Апи реализуется с помощью `FastAPI`. Эндпоинты:
* технические:
  * `/search_types` - выводит доступные методы поиска
  * `/corpora_info` - выводит информацию о корпусе
* `/search` - происзводит поиск и предоставляет его результаты. В проекте используется для выведеиния на сайт результатов поика
* взаимодействие пользователя с сайтом:
  * `/register` - регистрирует пользователя, записывает данные о нем в базу
  * `/login` - авторизует пользователя, проверяет валидность логина и пароля
  * `/profile/{user_login}` - выводыит данные о пользователи и сохраненные сообщения. В проекте данные выводятся на личную страницу
  * `/save` - добавляется сообщения в сохраненные пользователем. В проекте реализуется при нажатии на "лайк"
  * `/unsave` - удаляет сообщения из сохраненных. Применяется при нажатии на "дизлайк" в профиле

[Пример использования](https://github.com/hse-courses-tokubetsu/project-AnastasiaDobrynina/blob/main/Api%20Example.ipynb)

## База данных
* Схема БД
![sql_shema](https://github.com/hse-courses-tokubetsu/project-AnastasiaDobrynina/blob/main/drawSQL-image-export-2024-12-26%20(1).png)

* Подключение к базе данных Posgres происходит с помощью `psycopg2` и `SQL Alchemy`
* Данные добавляются вызовом файла [initdb.sql](https://github.com/hse-courses-tokubetsu/project-AnastasiaDobrynina/blob/main/db/initdb.sql)

Взаимодействие с базой данных:
* Запросы к таблице Users для регистрации, авторизации пользователя, и отображению личных данных в профиле
* Вызовы к таблицам Users, Saved и Text для отражения сохраненных сообщений
* Добавление и выполнение функций поиска по косинусной близости 

# Докер
Ссылки на докер-хаб:
* [Flask-приложение](https://hub.docker.com/repository/docker/anesthesia12/dubky_flask/general) (фронт-энд)
* [FastAPI](https://hub.docker.com/repository/docker/anesthesia12/dubky_fastapi/general) (бэкэнд)
* [база данных](https://hub.docker.com/repository/docker/anesthesia12/dubky_db/general)

Чтобы запустить приложении у себя необходимо скачать [docker-compose.yml](https://github.com/hse-courses-tokubetsu/project-AnastasiaDobrynina/blob/main/docker-compose.yml) и запустить команду в директории со скчанным файлом:
```
docker-compose up
```
Или запустите контейнеры по отдельности:
```
docker run -d -p 5000:5000 anesthesia12/dubky_fastapi
docker run -d -p 5000:5000 anesthesia12/dubky_flask
docker run -d -p 5000:5000 anesthesia12/dubky_db
```

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/lLCGRwL-)

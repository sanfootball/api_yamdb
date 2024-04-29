# api_yamdb
## Оглавление:
- [Стек технологий.](Стек-технологий)
- [Краткое описание проекта.](Краткое-описание-проекта)
- [Как запустить проект.](Как-запустить-проект)
- [Как наполнить БД данными](Как-наполнить-БД-данными)
- [Примеры запросов к API.](Примеры-запросов-к-API)
- [Доступ к документации по API](Доступ-к-документации-по-API)

## Стек технологий
- Python
- Django
- DRF
- JWT токены
- Проект написан на Linux

## Краткое описание проекта:
Данный проект является учебным и представляет из себя API с отзывами на книги, фильмы, песни итп.
У всех произведений есть категории и жанры.

В проекте есть несколько основных уровней доступа:
- Пользователь.
- Модератор.
- Администратор.

Пользователи могут:
- Регистрироваться.
- Создавать, редактировать и удалять свои отзывы на произведения.
- Комментировать отзывы.
- Редактировать и удалять свои комментарии.

Модераторы могут:
- Удалять и редактировать любы отзывы и комментарии (плюс все то, что могут пользователи).

Администраторы могут:
- Создавать новых пользователей.
- Создавать и удалять произведения, категории и жанры.

Основные цели проекта:
1. Потренироваться работать в команде, в том числе используя систему контроля версий git и ее онлайн репозиторий git hub.
2. Применить теоретичесие знания на практике, используя принцип API First.


## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:sanfootball/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
. venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Как наполнить БД данными:
Перейти в папку api_yamdb, где находится файл manage.py и дать команду на заполнение:

```
python manage.py csv_to_db
```


## Примеры запросов к API:

**Добавление нового отзыва**
Добавить новый отзыв. Пользователь может оставить только один отзыв на произведение. Права доступа: Аутентифицированные пользователи.

Вместо {title_id} указать номер интересующего произведения.
В поле оценка (score) указывается целое число от 1 до 10.
В поле текст (text) указывается текст отзыва.

Тип запроса: POST

#URL:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```
#Пример запроса:
{
  "text": "string",
  "score": 1
}

#Пример успешного ответа:
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}

**Получение комментария к отзыву**
Получить комментарий для отзыва по id. Права доступа: Доступно без токена.

Вместо {title_id} указать номер интересующего произведения.
Вместо {review_id} указать номер интересующего отзыва к произведению.
Вместо {comment_id} указать номер интересующего комментария к отзыву.

Тип запроса: GET

#URL:
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
#Пример ответа (успешный, код 200):
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}


## Доступ к документации по API:
Перейти в папку api_yamdb, где находится файл manage.py и выполнить команду:

```
python manage.py runserver
```
Далее в браузере ввести ссылку:
```
http://127.0.0.1:8000/redoc/
```


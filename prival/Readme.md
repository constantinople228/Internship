# REST API для работы с перевалом

Этот проект представляет собой REST API, разработанный для учета информации о перевалах. Он позволяет добавлять, просматривать, редактировать  информацию о перевалах.

## Задача проекта

Основная задача этого проекта - создать бэкенд для управления данными о перевалах. API предоставляет набор методов для работы с данными, такими как:
* добавление новой информации о перевале;
* получение подробной информации об отдельном перевале по его ID;
* редактирование информации о перевале;


## Реализованные функции

### 1. Добавление нового перевала (`POST /submitData/`)

Этот метод позволяет добавить новую запись о перевале в базу данных.

*   **Метод:** `POST`
*   **URL:** `http://127.0.0.1:8000/pereval/submitData/`
*   **Тело запроса (JSON):**
    ```json
    {
      "user": {
        "email": "user@example.com",
        "fam": "Иванов",
        "name": "Иван",
        "otc": "Иванович",
        "phone": "89991234567"
      },
      "coords": {
        "latitude": "45.1234",
        "longitude": "56.7890",
        "height": "1200"
      },
      "levels": {
        "winter": "1A",
        "summer": "2B",
        "autumn": null,
        "spring": null
      },
      "prival": {
        "date_added": "2023-01-15",
        "beauty_title": "Красивый перевал",
        "title": "Перевал",
        "other_titles": "Другое название",
        "connect": "Соединяет два ущелья"
      },
      "images": [
        {
          "img": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAA... (base64 encoded image data)"
        }
      ]
    }
    ```
    *   `user`: информация о пользователе.
    *   `coords`: координаты перевала (широта, долгота, высота).
    *   `levels`: категории сложности перевала по сезонам.
    *   `prival`: информация о перевале (дата добавления, название, описание, связь).
    *   `images`: массив изображений перевала в формате base64.
*   **Ответ (JSON):**
    ```json
    {
        "status": "success",
        "message": "Data added successfully",
        "pereval_id": 123
    }
    ```
   *  `status` : `success`, если запись добавлена, `error` если нет.
   * `message`: сообщение об ошибке или успехе.
   * `pereval_id`: ID добавленного перевала.

    * **Пример ответа при ошибке**:
     ```json
      {
        "status": "error",
        "message": "Недостающие поля в user"
      }
    ```

### 2. Получение информации об одном перевале по ID (`GET /submitData/<id>/`)

Этот метод позволяет получить подробную информацию о конкретном перевале по его идентификатору.

*   **Метод:** `GET`
*   **URL:** `http://127.0.0.1:8000/pereval/submitData/<id>/` (замените `<id>` на ID перевала).
*   **Ответ (JSON):**
    ```json
    {
      "user": ["user@example.com", "Иванов", "Иван", "Иванович", "89991234567"],
      "coords": ["45.1234", "56.7890", "1200"],
      "levels": ["1A", "2B", null, null],
      "prival": [1,"user_id", "coord_id", "level_id", "2023-01-15","Красивый перевал","Перевал","Другое название", "Соединяет два ущелья", "new"],
      "images": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAA..."]
    }
    ```
   * `user`: информация о пользователе
   *  `coords`: координаты перевала
   * `levels`: уровни сложности перевала
   * `prival`: информация о перевале
   * `images`: изображения перевала
* **Ответ при ошибке**:
    ```json
    {
      "state": 0,
      "message": "Перевал не найден"
     }
    ```

### 3. Редактирование информации о перевале (`PATCH /submitData/update/<id>/`)

Этот метод позволяет изменить информацию о перевале. Перевал должен быть в статусе "new".

*   **Метод:** `PATCH`
*   **URL:** `http://127.0.0.1:8000/pereval/submitData/update/<id>/` (замените `<id>` на ID перевала).
*   **Тело запроса (JSON):**
    ```json
        {
          "coords": {
            "latitude": "45.1234",
            "longitude": "56.7890",
            "height": "1200"
          },
          "levels": {
            "winter": "1B",
            "summer": "2A",
            "autumn": null,
            "spring": null
          },
          "prival": {
            "date_added": "2023-01-16",
            "beauty_title": "Обновленный перевал",
            "title": "Новое название перевала",
            "other_titles": "Другое название",
            "connect": "Соединяет три ущелья"
          },
        "images": [
            {
                "img": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAA... (base64 encoded image data)"
            }
        ]
    }
    ```
    *   JSON должен содержать все необходимые поля (`coords`, `levels`, `prival`, `images`).
    *  Можно изменять все поля кроме полей пользователя.
*   **Ответ (JSON):**
    ```json
    {
      "state": 1,
      "message": "Data updated successfully"
    }
    ```
    *   `state`: `1`, если обновление прошло успешно, `0` - если нет.
    *   `message`: сообщение об ошибке или успехе.
* **Пример ответа при ошибке**:
    ```json
     {
         "state": 0,
         "message": "Перевал не в статусе new"
     }
    ```


### Зависимости
*   `Django`
*   `djangorestframework`
*   `psycopg2`
*   `python-dotenv`

### Настройка
1. Создать базу данных PostgreSQL
2. Добавить настройки базы данных в файл `.env` (смотри `.env.example`).
3.  Установить зависимости: `pip install -r requirements.txt`
4. Применить миграции `python manage.py migrate`.
5. Запустить сервер: `python manage.py runserver`

## Как использовать API

Для работы с API можно использовать:
* cURL
* Postman
* Python `requests`
* Другие инструменты

**Пример запроса cURL (получение перевала по ID):**

```bash
curl -X GET http://127.0.0.1:8000/pereval/submitData/1/
```
**Пример запроса cURL (редактирование перевала по ID):**
```bash
curl -X PATCH \
-H "Content-Type: application/json" \
-d '{"coords": {"latitude": "40.7128", "longitude": "-74.0060", "height": "100"}, "levels": {"winter": "1A", "summer": "2B", "autumn": null, "spring": null}, "prival": {"date_added": "2024-12-20", "beauty_title": "Красота", "title": "Замечательный перевал", "other_titles": "Другое название", "connect": "Соединяет реки"}, "images": []}' \
http://127.0.0.1:8000/pereval/submitData/update/1/
```


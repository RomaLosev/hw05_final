# YATUBE
Социальная сеть

# Описание
Благодаря этому проекту можно создавать посты, оставлять комментарии под постами и подписываться на понравившихся авторов.

# Технологии

### Python, Django, Pillow, sorl-thumbnail, Bootstrap.

___
# Запуск проекта в dev-режиме

Клонируйте репозиторий
```
git clone [link]
```

# Установите и активируйте виртуальное окружение:
___
#### Для пользователей Windows:
```
python -m venv venv
source venv/scripts/activate
python -m pip install --upgrade pip
```
#### Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
```
#### Перейдите в каталог с файлом manage.py и выполните команды: 

#### Выполнить миграции:
```
python manage.py migrate
```
#### Создайте супер-пользователя:
```
python manage.py createsuperuser
```
#### Соберите статику:
```
python manage.py collectstatic
```

# Запуск проекта:
```
python manage.py runserver
```
По умолчанию для неавторизованных пользователей проект доступен только для чтения.

### Автор:
[Roman Losev](https://github.com/RomaLosev)

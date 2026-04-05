Фастфуд 24 - Сервис онлайн-доставки еды

Backend: Django,
Frontend: HTML + CSS + js,
DB: PostgreSQL

Развертывание:
Установить PostgreSQL
Настроить переменную окружения .env в соответствии с .env.example
Создать базу данных в соответствии с указанным названием в .env

Запуск проекта:
python -m venv venv
source venv/bin/activate (venv\Scripts\activate для Windows)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser (админский аккаунт)
python manage.py runserver
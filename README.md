Фастфуд 24 - Сервис онлайн-доставки еды

Backend: Django
Frontend: HTML + CSS + js,
DB: PostgreSQL

Развертывание:

1. В корне проекта создайте файл .env по образцу из .env.example. Заполните все его поля нужным образом как в примере. Для генерации ключей рекомендуется воспользоваться следующими командаами:

# SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
# ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

2. Установите PostgreSQL
Для Linux:
sudo -u postgres psql
В консоли psql выполняется следующее:
CREATE DATABASE fastfood24;
ALTER USER postgres WITH PASSWORD 'your_db_password';
\q

Для Windows:
Откройте pgAdmin или Powershell. Если powershell, выполните "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
Далее выполните те же команды, что и для Linux

3. Виртуальное окружение и зависимости
python3 -m venv venv (pytnon -m venv venv)
source venv/bin/activate (venv\Scripts\activate для windows)
pip install --upgrade pip
pip install -r requirements.txt

4. Убедившись, что виртуальное окружение открыто, выполните:
python manage.py migrate
python manage.py createsuperuser

5. Запустите сервер командой python manage.py runserver

6. Откройте в браузере http://127.0.0.1:8000/

7. Для перехода в админскую панель добавьте /admin. Для входа введите данные созданного ранее суперпользователя

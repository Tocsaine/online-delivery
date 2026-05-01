import os
import sys
import django

# 1. Настраиваем пути (чтобы Django нашёл проект)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection, OperationalError

print("Проверка сырых данных в базе данных (без расшифровки)...")
print("-" * 50)


def check_table(table_name, column_name):
    try:
        with connection.cursor() as cursor:
            # Выполняем прямой запрос к БД
            cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
            row = cursor.fetchone()

            if row and row[0]:
                raw_value = row[0]
                # Проверяем, начинается ли значение с сигнатуры Fernet 'gAAAA'
                # (для строк) или если это байты (для BinaryField)
                val_str = raw_value.decode('utf-8', errors='ignore') if isinstance(raw_value, bytes) else str(raw_value)

                if val_str.startswith('gAAAA') or len(val_str) > 100:
                    print(f"Таблица {table_name} ({column_name}): ЗАШИФРОВАНО")
                    print(f"   Содержимое (первые 20 символов): {val_str[:20]}...")
                else:
                    print(f"Таблица {table_name} ({column_name}): ОТКРЫТЫЙ ТЕКСТ")
                    print(f"   Содержимое: {val_str}")
            else:
                print(f"Таблица {table_name}: Нет данных для проверки")
    except OperationalError as e:
        print(f"Ошибка доступа к таблице {table_name} (возможно, она не создана): {e}")


# 2. Проверяем ключевые поля
print("\nПроверка профилей пользователей:")
check_table("accounts_profile", "phone")

print("\nПроверка адресов пользователей:")
check_table("accounts_address", "text")

print("\nПроверка заказов:")
check_table("orders_order", "phone")
check_table("orders_order", "address")

print("-" * 50)
print("Готово!")
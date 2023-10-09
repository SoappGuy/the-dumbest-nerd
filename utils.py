import sqlite3


# Функція для створення вайтлисту для нової групи
def create_whitelist_table(chat_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Створить таблицю, якщо вона ще не існує
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS whitelists_{abs(int(chat_id))}
                          (command TEXT PRIMARY KEY,
                           user_id INTEGER)''')

    conn.commit()
    conn.close()


# Додати користувача у вайтлист для певної групи
def add_user_to_whitelist_db(chat_id, command, user_id):
    create_whitelist_table(chat_id) # Створити новий вайтлист якщо треба

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Додасть користувача до вайтлисту
    cursor.execute(f"INSERT INTO whitelists_{abs(int(chat_id))} (command, user_id) VALUES (?, ?)",
                   (command, user_id))

    conn.commit()
    conn.close()


# Видалити користувача з вайтлисту для певної групи
def remove_user_from_whitelist_db(chat_id, command, user_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Видалить користувача з вайтлисту
    cursor.execute(f"DELETE FROM whitelists_{abs(int(chat_id))} WHERE command = ? AND user_id = ?",
                   (command, user_id))

    conn.commit()
    conn.close()


# Перевірити чи користувач знаходиться у вайтлисті
def is_user_in_whitelist(chat_id, command, user_id):
    create_whitelist_table(chat_id)  # Створити новий вайтлист якщо треба

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Перевірить, чи користувач знаходиться в вайтлисті
    cursor.execute(f"SELECT 1 FROM whitelists_{abs(int(chat_id))} WHERE command = ? AND user_id = ?",
                   (command, user_id))
    result = cursor.fetchone()

    conn.close()

    return result is not None


# Функція для створення таблиці для нової групи
def create_group_table(chat_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Створить таблицю для групи, якщо вона ще не існує
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS chat_{abs(int(chat_id))}
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       message_text TEXT,
                       sender TEXT,
                       timestamp DATETIME)''')

    conn.commit()
    conn.close()


# Функція для збереження повідомлення у базу даних
def save_message_to_db(message_text, sender, timestamp, chat_id):
    create_group_table(chat_id)  # Створити таблицю для групи (якщо потрібно)

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Вставка нового повідомлення у відповідну таблицю групи
    cursor.execute(f"INSERT INTO chat_{abs(int(chat_id))} (message_text, sender, timestamp) VALUES (?, ?, ?)",
                   (message_text, sender, timestamp))

    conn.commit()
    conn.close()


# Функція для зчитування останніх N повідомлень з бази даних
def get_last_n_messages(n, chat_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Зчитування останніх N повідомлень
    cursor.execute(f"SELECT * FROM chat_{abs(int(chat_id))} ORDER BY timestamp DESC LIMIT ?",
                   (n,))

    db = cursor.fetchall()

    conn.close()

    return db


# Функція для отримання всіх вайтлистів з бази даних
def get_all_whitelists(chat_id):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Виконає SQL-запит для отримання всіх вайтлистів
    cursor.execute(f"SELECT command, user_id FROM whitelists_{abs(int(chat_id))}")

    rows = cursor.fetchall()
    conn.close()

    # Поверне результат у вигляді списку кортежів (command, user_id)
    return rows


# Сам розберешся
def get_args(event):
    text = event.text
    args = text.split()[1:]
    return args
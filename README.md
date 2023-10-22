# Проект по базе данных с использованием hh.ru 
Этот проект представляет собой инструмент для сбора и анализа данных о компаниях и вакансиях с использованием hh.ru API. Данные сохраняются в базе данных PostgreSQL, а предоставленные функции позволяют проводить различные запросы к данным.

## Запуск проекта

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/dikiypes/kurs-5.git
   cd hhru-database-project

2. Установить зависимости:
    ```bash
    pip install -r requirements.txt

3. Создать файл config.py с параметрами подключения к базе данных (dbname, user, password, host, port).
4. Запустить основной файл
    ```bash
    python main.py


# Использование класса DBManager
```
from db_manager import DBManager

# Создание экземпляра DBManager
db_manager = DBManager(dbname='your_db_name', user='your_username', password='your_password', host='your_host', port='your_port')

# Создание таблиц
db_manager.create_tables()

# Вставка данных по компании
db_manager.insert_data_by_company('Company Name')

# Запрос данных
companies_and_vacancies = db_manager.get_companies_and_vacancies_count()
all_vacancies = db_manager.get_all_vacancies()
avg_salary = db_manager.get_avg_salary()
high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
keyword_vacancies = db_manager.get_vacancies_with_keyword('Python')

# Вывод результатов
print('Companies and Vacancies:', companies_and_vacancies)
print('All Vacancies:', all_vacancies)
print('Average Salary:', avg_salary)
print('High Salary Vacancies:', high_salary_vacancies)
print('Keyword Vacancies:', keyword_vacancies)

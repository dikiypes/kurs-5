import requests
import psycopg2
import time
import random
import config


class DBManager:
    def __init__(self, dbname, user, password, host, port):
        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # Создание таблицы companies
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        # Создание таблицы vacancies
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id),
                name TEXT NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url TEXT,
                area_name VARCHAR(255),
                CONSTRAINT fk_company_id FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
            )
        ''')

        self.conn.commit()

    def insert_data_by_company(self, company_name):
        base_url = 'https://api.hh.ru'
        vacancies_url = f'{base_url}/vacancies'

        company_search_url = f'{base_url}/employers'
        company_params = {'text': company_name,
                          'search_field': 'name', 'page': 0}
        company_response = requests.get(
            company_search_url, params=company_params)
        result = []
        page = 0
        while True:
            if company_response.status_code == 200:
                company_data = company_response.json()
                if company_data['found'] > 0:
                    # Получение списка вакансий компании
                    company_id = company_data['items'][0]['id']
                    vacancies_params = {'employer_id': company_id,
                                        'per_page': 100, 'page': page}
                    vacancies_response = requests.get(
                        vacancies_url, params=vacancies_params)

                    if vacancies_response.status_code == 200:
                        vacancies_data = vacancies_response.json()
                        if len(vacancies_data['items']) > 0:
                            for vacancie in vacancies_data['items']:
                                result.append(vacancie)
                            print(f'vacancies {company_name} from page {page} add')
                            page += 1
                        else:
                            break
                    else:
                        print(f'Failed to fetch vacancies. Status Code: {vacancies_response.status_code}')
                else:
                    print(f'No company found with the name: {company_name}')
            else:
                print(f'Failed to fetch company data. Status Code: {company_response.status_code}')
            time.sleep(random.randint(1, 5))

        self.cursor.execute(
            '''INSERT INTO companies (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING''', (company_id, company_name))

        for vacancy in result:
            vacancy_id = vacancy.get('id')
            vacancy_name = vacancy.get('name')
            vacancy_url = vacancy.get('alternate_url')
            area_name = vacancy.get('area', {}).get('name')

            salary = vacancy.get('salary', {})
            if salary:
                salary_from = salary.get('from')
                salary_to = salary.get('to')
            else:
                salary_from = None
                salary_to = None

            employer = vacancy.get('employer', {})
            employer_id = employer.get('id')
            employer_name = employer.get('name')

            self.cursor.execute('''
    INSERT INTO vacancies (id, company_id, name, salary_from, salary_to, url, area_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING
''', (vacancy_id, employer_id, vacancy_name, salary_from, salary_to or None, vacancy_url, area_name))

        self.conn.commit()

    def get_companies_and_vacancies_count(self):
        self.cursor.execute('''
            SELECT companies.name, COUNT(vacancies.id) as vacancy_count
            FROM companies
            LEFT JOIN vacancies ON companies.id = vacancies.company_id
            GROUP BY companies.id, companies.name
        ''')
        return self.cursor.fetchall()

    def get_all_vacancies(self):
        self.cursor.execute('''
            SELECT companies.name as company_name, vacancies.name as vacancy_name,
                   vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN companies ON vacancies.company_id = companies.id
        ''')
        return self.cursor.fetchall()

    def get_avg_salary(self):
        self.cursor.execute('''
            SELECT AVG(salary_from + salary_to) / 2 as avg_salary
            FROM vacancies
        ''')
        return self.cursor.fetchone()[0]

    def get_vacancies_with_higher_salary(self):
        avg_salary = self.get_avg_salary()
        self.cursor.execute('''
            SELECT name, salary_from, salary_to, url
            FROM vacancies
            WHERE (salary_from + salary_to) / 2 > %s
        ''', (avg_salary,))
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        self.cursor.execute('''
            SELECT companies.name as company_name, vacancies.name as vacancy_name,
                   vacancies.salary_from, vacancies.salary_to, vacancies.url
            FROM vacancies
            JOIN companies ON vacancies.company_id = companies.id
            WHERE vacancies.name ILIKE %s
        ''', ('%' + keyword + '%',))
        return self.cursor.fetchall()


if __name__ == "__main__":
    companys = ['Домклик', 'URSiP', 'Точка',
                'Remokate', '7RedLines', 'FunBox', 'getmatch', 'MX21', 'Автостэлс', 'Skyeng']

    db_manager = DBManager(dbname=config.dbname, user=config.user,
                           password=config.password, host=config.host, port=config.port)
    db_manager.create_tables()

    for company_name in companys:
        db_manager.insert_data_by_company(company_name)

    companies_and_vacancies = db_manager.get_companies_and_vacancies_count()
    all_vacancies = db_manager.get_all_vacancies()
    avg_salary = db_manager.get_avg_salary()
    high_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
    keyword_vacancies = db_manager.get_vacancies_with_keyword('python')
    print('companies_and_vacancies', companies_and_vacancies)
    print('all_vacancies:', all_vacancies)
    print('avg_salary:', avg_salary)
    print('high_salary_vacancies:', high_salary_vacancies)
    print('keyword_vacancies:', keyword_vacancies)

import requests
from pprint import pprint
import math
from dotenv import load_dotenv
import os

COEFFICIENT_LOWER_SALARY = 1.2
COEFFICIENT_HIGHER_SALARY = 0.8


def main():
    load_dotenv()
    superjob_token = os.environ['SUPERJOB_TOKEN']
    programming_languages = ['python', 'java', 'javascript', 'C#', 'C++', 'PHP', 'Typescript', 'Ruby']
    # fetch_headhunter_vacancies(programming_languages)
    fetch_superjob_vacancies(programming_languages, superjob_token)


def fetch_superjob_vacancies(programming_languages, superjob_token):
    results_number = 100
    params = {
        'keywords[1][srws]': 1,
        'keywords[1][skws]': 'or',
        'keywords[1][keys]': '',
        'page': 0,
        'count': results_number,
        'catalogues': 48,
        'town': 4
    }

    headers = {
        'X-Api-App-Id': superjob_token
    }

    vacancy_statistics = {}
    for programming_language in programming_languages:
        print(programming_language)
        vacancies, vacancies_found = fetch_vacancies_for_programming_language_superjob(headers, params,
                                                                                       programming_language)
        vacancy_statistics[programming_language] = calculate_average_salary_for_superjob(vacancies, vacancies_found)
    pprint(vacancy_statistics)


def fetch_vacancies_for_programming_language_superjob(headers, params, programming_language):
    params['keywords[1][keys]'] = programming_language
    page = 0
    pages_number = 1
    vacancies = []
    vacancies_found = 0
    while page < pages_number:
        params['page'] = page
        print(f'processed page {page}')
        response = requests.get('https://api.superjob.ru/2.0/vacancies', params=params, headers=headers)
        response.raise_for_status()
        review_result = response.json()
        vacancies.extend(review_result['objects'])
        vacancies_found = review_result['total']
        pages_number = math.ceil(vacancies_found / 100)
        page += 1
    return vacancies, vacancies_found


def predict_rub_salary_for_superjob(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def fetch_headhunter_vacancies(programming_languages):
    params = {
        'area': 1,
        'specialization': '1.221',
        'period': 30,
        'page': 0,
        'per_page': 100,
        'text': ''
    }
    vacancy_statistics = {}
    for programming_language in programming_languages:
        print(programming_language)
        vacancies, vacancies_found = fetch_vacancies(programming_language, params)
        vacancy_statistics[programming_language] = calculate_average_salary(vacancies, vacancies_found)
    pprint(vacancy_statistics)


def fetch_vacancies(programming_language, params):
    params['text'] = programming_language

    page = 0
    pages_number = 1
    vacancies_found = 0
    vacancies = []
    while page < pages_number:
        params['page'] = page
        print(f'processed page {page}')
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        response.raise_for_status()
        review_result = response.json()
        vacancies.extend(review_result['items'])
        pages_number = review_result['pages']
        vacancies_found = review_result['found']
        page += 1
    return vacancies, vacancies_found


def calculate_average_salary(vacancies, vacancies_found):
    average_salaries = {'vacancies_found': vacancies_found}
    salaries = []
    for vacancy in vacancies:
        expected_salary = predict_rub_salary(vacancy)
        if expected_salary:
            salaries.append(expected_salary)
    average_salaries['vacancies_processed'] = len(salaries)
    average_salaries['average_salary'] = int(sum(salaries) / len(salaries))
    return average_salaries


def calculate_average_salary_for_superjob(vacancies, vacancies_found):
    average_salaries = {'vacancies_found': vacancies_found}
    salaries = []
    for vacancy in vacancies:
        expected_salary = predict_rub_salary_for_superjob(vacancy)
        if expected_salary:
            salaries.append(expected_salary)
    average_salaries['vacancies_processed'] = len(salaries)
    average_salaries['average_salary'] = int(sum(salaries) / len(salaries))
    return average_salaries


def predict_rub_salary(vacancy):
    if not vacancy['salary']:
        return None
    if vacancy['salary']['currency'] != 'RUR':
        return None
    return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from and not salary_to:
        return salary_from * COEFFICIENT_LOWER_SALARY
    elif not salary_from and salary_to:
        return salary_to * COEFFICIENT_HIGHER_SALARY


if __name__ == '__main__':
    main()

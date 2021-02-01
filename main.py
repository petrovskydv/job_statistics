import logging
import math
import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

logger = logging.getLogger(__name__)

COEFFICIENT_LOWER_SALARY = 1.2
COEFFICIENT_HIGHER_SALARY = 0.8
RESULTS_ON_PAGE_NUMBER = 100


def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger.setLevel(logging.INFO)

    load_dotenv()
    superjob_token = os.environ['SUPERJOB_TOKEN']

    programming_languages = ['python', 'java', 'javascript', 'C#', 'C++', 'PHP', 'Typescript', 'Ruby']

    headhunter_region = 1
    headhunter_specialization = '1.221'
    vacancy_publication_period = 30
    superjob_region = 4
    superjob_specialization = 48

    logger.info('getting statistics for HeadHunter')
    headhunter_languages_statistics = fetch_headhunter_vacancy_statistics(
        programming_languages, headhunter_region, headhunter_specialization, vacancy_publication_period)
    logger.info('getting statistics for SuperJob')
    superjob_languages_statistics = fetch_superjob_vacancy_statistics(
        programming_languages, superjob_token, superjob_specialization, superjob_region)
    show_statistics(headhunter_languages_statistics, 'HeadHunter Moscow')
    show_statistics(superjob_languages_statistics, 'SuperJob Moscow')


def fetch_headhunter_vacancy_statistics(
        programming_languages, headhunter_region, headhunter_specialization, vacancy_publication_period):
    params = {
        'area': headhunter_region,
        'specialization': headhunter_specialization,
        'period': vacancy_publication_period,
        'per_page': RESULTS_ON_PAGE_NUMBER,
    }
    vacancy_statistics = {}
    for programming_language in programming_languages:
        logger.debug(programming_language)
        vacancies, vacancies_found = fetch_vacancies_for_programming_language_for_headhunter(
            programming_language, params)
        vacancy_statistics[programming_language] = fetch_statistics_for_programming_language(
            vacancies, vacancies_found, predict_rub_salary_for_headhunter)
    return vacancy_statistics


def fetch_vacancies_for_programming_language_for_headhunter(programming_language, params):
    params['text'] = programming_language
    page = 0
    pages_number = 1
    vacancies_found = 0
    vacancies = []
    while page < pages_number:
        params['page'] = page
        response = requests.get('https://api.hh.ru/vacancies', params=params)
        response.raise_for_status()
        review_result = response.json()
        vacancies.extend(review_result['items'])
        logger.debug(f'processed page {page}')
        pages_number = review_result['pages']
        vacancies_found = review_result['found']
        page += 1
    return vacancies, vacancies_found


def fetch_superjob_vacancy_statistics(
        programming_languages, superjob_token, superjob_specialization, superjob_region):
    params = {
        'keywords[1][srws]': 1,
        'keywords[1][skws]': 'or',
        'count': RESULTS_ON_PAGE_NUMBER,
        'catalogues': superjob_specialization,
        'town': superjob_region
    }

    headers = {
        'X-Api-App-Id': superjob_token
    }

    vacancy_statistics = {}
    for programming_language in programming_languages:
        logger.debug(programming_language)
        vacancies, vacancies_found = fetch_vacancies_for_programming_language_for_superjob(
            headers, params, programming_language)
        vacancy_statistics[programming_language] = fetch_statistics_for_programming_language(
            vacancies, vacancies_found, predict_rub_salary_for_superjob)
    return vacancy_statistics


def fetch_vacancies_for_programming_language_for_superjob(headers, params, programming_language):
    params['keywords[1][keys]'] = programming_language
    page = 0
    pages_number = 1
    vacancies = []
    vacancies_found = 0
    while page < pages_number:
        params['page'] = page
        response = requests.get('https://api.superjob.ru/2.0/vacancies', params=params, headers=headers)
        response.raise_for_status()
        review_result = response.json()
        vacancies.extend(review_result['objects'])
        logger.debug(f'processed page {page}')
        vacancies_found = review_result['total']
        pages_number = math.ceil(vacancies_found / RESULTS_ON_PAGE_NUMBER)
        page += 1
    return vacancies, vacancies_found


def fetch_statistics_for_programming_language(vacancies, vacancies_found, callback):
    average_salaries = {'vacancies_found': vacancies_found}
    salaries = []
    for vacancy in vacancies:
        expected_salary = callback(vacancy)
        if expected_salary:
            salaries.append(expected_salary)
    average_salaries['vacancies_processed'] = len(salaries)
    average_salaries['average_salary'] = int(sum(salaries) / len(salaries))
    return average_salaries


def predict_rub_salary_for_superjob(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_rub_salary_for_headhunter(vacancy):
    if not vacancy['salary']:
        return None
    if vacancy['salary']['currency'] != 'RUR':
        return None
    return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def predict_salary(salary_from, salary_to):
    if salary_from is not None and salary_to is not None:
        return (salary_from + salary_to) / 2
    elif salary_from is not None and salary_to is None:
        return salary_from * COEFFICIENT_LOWER_SALARY
    elif salary_from is None and salary_to is not None:
        return salary_to * COEFFICIENT_HIGHER_SALARY


def show_statistics(vacancies, title):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for programming_language, statistic in vacancies.items():
        table_data.append(
            [
                programming_language,
                statistic['vacancies_found'],
                statistic['vacancies_processed'],
                statistic['average_salary']
            ]
        )
    table = AsciiTable(table_data, title)
    print()
    print(table.table)


if __name__ == '__main__':
    main()

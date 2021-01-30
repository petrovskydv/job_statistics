import requests
from pprint import pprint
import math

COEFFICIENT_LOWER_SALARY = 1.2
COEFFICIENT_HIGHER_SALARY = 0.8


def main():
    programming_languages = ['python', 'java', 'javascript', 'C#', 'C++', 'PHP', 'Typescript', 'Ruby']
    # fetch_headhunter_vacancies(programming_languages)
    fetch_superjob_vacancies(programming_languages)


def fetch_superjob_vacancies(programming_languages):
    results_number = 100
    params = {
        'keywords[1][srws]': 1,
        'keywords[1][skws]': '',
        'keywords[1][keys]': '',
        'page': 0,
        'count': results_number,
        'catalogues': 48,
        'town': 4
    }

    headers = {
        'X-Api-App-Id': 'v3.r.15222203.452d44010b7ce1097d1d6b3c2a3bf13204c0cf9b.c438b5820baa0e0d31d95ffde59c54bf70c0c618'
    }

    page = 0
    pages_number = 1
    vacancies = []
    while page < pages_number:
        params['page'] = page
        print(f'processed page {page}')
        response = requests.get('https://api.superjob.ru/2.0/vacancies', params=params, headers=headers)
        response.raise_for_status()
        review_result = response.json()
        # pprint(review_result)
        vacancies.extend(review_result['objects'])
        vacancies_found = review_result['total']
        pages_number = math.ceil(vacancies_found / results_number)
        page += 1
        for vacancy in vacancies:
            print(vacancy['profession'], vacancy['town']['title'])


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


def predict_rub_salary(vacancy):
    if not vacancy['salary']:
        return None
    from_salary = vacancy['salary']['from']
    to_salary = vacancy['salary']['to']

    if vacancy['salary']['currency'] != 'RUR':
        return None
    if from_salary and to_salary:
        return (from_salary + to_salary) / 2
    elif from_salary and not to_salary:
        return from_salary * COEFFICIENT_LOWER_SALARY
    elif not from_salary and to_salary:
        return to_salary * COEFFICIENT_HIGHER_SALARY


if __name__ == '__main__':
    main()

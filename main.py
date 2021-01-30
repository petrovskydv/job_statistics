import requests
from pprint import pprint


def main():
    programming_languages = ['python', 'java', 'javascript', 'C#', 'C++', 'PHP', 'Typescript', 'Ruby']
    # programming_languages = ['python']
    vacancy_statistics = {}
    for programming_language in programming_languages:
        vacancy_statistics[programming_language] = fetch_vacancies(programming_language)
    pprint(vacancy_statistics)


def fetch_vacancies(programming_language):
    params = {
        'area': 1,
        'specialization': '1.221',
        'period': 30,
        'text': programming_language
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    review_result = response.json()
    average_salaries = {}
    average_salaries['vacancies_found'] = review_result['found']
    salaries = []
    for vacancy in review_result['items']:
        expected_salary = predict_rub_salary(vacancy)
        if expected_salary:
            salaries.append(expected_salary)
    average_salaries['vacancies_processed'] = len(salaries)
    average_salaries['average_salary'] = int(sum(salaries) / len(salaries))
    pprint(average_salaries)
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
        return from_salary * 1.2
    elif not from_salary and to_salary:
        return to_salary * 0.8


if __name__ == '__main__':
    main()

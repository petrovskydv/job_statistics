import requests
from pprint import pprint


def main():
    # programming_languages = ['python', 'java', 'javascript', 'C#', 'C++', 'PHP', 'Typescript', 'Ruby']
    programming_languages = ['python']
    for programming_language in programming_languages:
        fetch_vacancies(programming_language)


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
    for vacancy in review_result['items']:
        pprint(vacancy['salary'])


if __name__ == '__main__':
    main()

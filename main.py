import requests
from pprint import pprint
import json


def main():
    params = {
        'area': 1,
        'specialization': '1.221',
        'period': 30
    }
    response = requests.get('https://api.hh.ru/vacancies', params=params)
    response.raise_for_status()
    review_result = response.json()
    pprint(review_result)


if __name__ == '__main__':
    main()

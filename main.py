import requests
import decouple
from terminaltables import AsciiTable


LANGUAGES = ("Python", "Java", "Javascript", "C++", "C#", "Ruby", "Go",)


def draw_table(payload, name):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            'Средняя зарплата',
        ],
    ]
    for language, stats in payload.items():
        row = []
        row.append(language)
        row.append(stats["vacancies_found"])
        row.append(stats["vacancies_processed"])
        row.append(stats["average_salary"])
        table_data.append(row)
    table_instance = AsciiTable(table_data, name)
    print(table_instance.table)


def calculate_salary(payment_from, payment_to):
    if not payment_from:
        return payment_to * 0.8
    if not payment_to:
        return payment_from * 1.2
    return (payment_from + payment_to) / 2


def predict_rub_salary_for_superJob(vacancy):
    if vacancy["payment_from"] or vacancy["payment_to"]:
        if vacancy["currency"] == "rub":
            return calculate_salary(vacancy["payment_from"], vacancy["payment_to"])
    return None


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy["salary"]
    if salary:
        if salary["currency"] == "RUR":
            return calculate_salary(salary["from"], salary["to"])
    return None


def get_vacancies_stats_for_hh():
    language_stats = {}
    for language in LANGUAGES:
        hh_response = requests.get("https://api.hh.ru/vacancies", params={'text': language, 'area': 1})
        hh_response.raise_for_status()

        page = 0
        pages_number = 1
        all_pages = []
        while page < pages_number:
            page_response = requests.get(hh_response.url, params={'page': page})
            page_response.raise_for_status()
            page_payload = page_response.json()
            all_pages.append(page_payload)

            pages_number = page_payload["pages"]
            page += 1

        count = 0
        salary_sum = 0
        for vacancies in all_pages:
            for vacancy in vacancies["items"]:
                predicted_salary = predict_rub_salary_for_hh(vacancy)
                if predicted_salary:
                    count += 1
                    salary_sum += predicted_salary
            try:
                average_salary = int(salary_sum/count)
            except ZeroDivisionError:
                average_salary = 0

            language_stats[language] = {}
            language_stats[language]["vacancies_found"] = vacancies["found"]
            language_stats[language]["vacancies_processed"] = count
            language_stats[language]["average_salary"] = average_salary

    return language_stats


def get_vacancies_stats_for_superjob(token):
    sj_url = "https://api.superjob.ru/2.0/vacancies"
    headers = {
        'X-Api-App-Id': token
    }
    language_stats = {}
    for language in LANGUAGES:
        superjob_response = requests.get(sj_url, headers=headers, params={'keyword': language, 'town': 4})
        superjob_response.raise_for_status()
        page_payload = superjob_response.json()

        count = 0
        salary_sum = 0
        page = 1
        all_pages = []
        all_pages.append(page_payload)
        while page_payload["more"]:
            page_response = requests.get(superjob_response.url, headers=headers, params={"page": page})
            page_response.raise_for_status()
            page_payload = page_response.json()
            all_pages.append(page_payload)
            page += 1

        for page in all_pages:
            for vacancy in page["objects"]:
                predicted_salary = predict_rub_salary_for_superJob(vacancy)
                if predicted_salary:
                    count += 1
                    salary_sum += predicted_salary
            try:
                average_salary = int(salary_sum/count)
            except ZeroDivisionError:
                average_salary = 0

            language_stats[language] = {}
            language_stats[language]["vacancies_found"] = page_payload["total"]
            language_stats[language]["vacancies_processed"] = count
            language_stats[language]["average_salary"] = average_salary
    return language_stats


def main():
    token = decouple.config('SUPER_JOB_TOKEN')
    superjob_stats = get_vacancies_stats_for_superjob(token)
    draw_table(superjob_stats, "SuperJob Moscow")

    print()
    hh_stats = get_vacancies_stats_for_hh()
    draw_table(hh_stats, "HeadHunter Moscow")


if __name__ == '__main__':
    main()

import requests
import decouple
from terminaltables import AsciiTable


def draw_table(payload, name):
    table_data = [
                ["Язык программирования", "Вакансий найдено", "Вакансий обработано", 'Средняя зарплата']
            ]
    for language in payload:
        new_row = []
        new_row.append(language)
        new_row.append(payload[language]["vacancies_found"])
        new_row.append(payload[language]["vacancies_processed"])
        new_row.append(payload[language]["average_salary"])
        table_data.append(new_row)
    table_instance = AsciiTable(table_data, name)
    print(table_instance.table)


def predict_rub_salary_for_superJob(vacancy):
    if vacancy["payment_from"] != 0 or vacancy["payment_to"] != 0:
        if vacancy["payment_from"] == 0:
            return vacancy["payment_to"]*0.8
        if vacancy["payment_to"] == 0:
            return vacancy["payment_from"]*1.2
        return (vacancy["payment_from"]+vacancy["payment_to"])/2
    return None


def predict_rub_salary_for_hh(vacancy):
    salary = vacancy["salary"]
    if salary is not None:
        if salary["currency"] != "RUR":
            return None
        if salary["from"] is None:
            return salary["to"]*0.8
        if salary["to"] is None:
            return salary["from"]*1.2
        return (salary["from"]+salary["to"])/2
    return None


def get_vacancies_for_hh():
    hh_payloads = [
        {
            "text": "Python",
            "area": 1,
            },
        {
            "text": "Java",
            "area": 1,
            },
        {
            "text": "Javascript",
            "area": 1,
            },
        {
            "text": "C++",
            "area": 1,
            },
        {
            "text": "C#",
            "area": 1,
            },
        {
            "text": "Ruby",
            "area": 1,
            },
        {
            "text": "Go",
            "area": 1,
            },
    ]
    hh_result = {}
    for payload in hh_payloads:
        language_response = requests.get("https://api.hh.ru/vacancies", params=payload)
        language_response.raise_for_status()

        page = 0
        pages_number = 1
        result_page = []
        while page < pages_number:
            page_response = requests.get(language_response.url, params={'page': page})
            page_response.raise_for_status()
            page_payload = page_response.json()
            result_page.append(page_payload)

            pages_number = page_payload["pages"]
            page += 1

        count = 0
        salary_sum = 0
        for vacancies in result_page:
            for vacancy in vacancies["items"]:
                if predict_rub_salary_for_hh(vacancy) is not None:
                    count += 1
                    salary_sum += predict_rub_salary_for_hh(vacancy)
            average_salary = salary_sum/count
            new_data = {
                payload["text"]: {
                    "vacancies_found": vacancies["found"],
                    "vacancies_processed": count,
                    "average_salary": int(average_salary),
                }
            }
            hh_result.update(new_data)

    return hh_result


def get_vacancies_for_superjob(token):
    sj_url = "https://api.superjob.ru/2.0/vacancies"
    headers = {
        'X-Api-App-Id': token
    }
    superjob_payloads = [
        {
            "keyword": "Python",
            "town": 4,
        },
        {
            "keyword": "Java",
            "town": 4,
        },
        {
            "keyword": "Javascript",
            "town": 4,
        },
        {
            "keyword": "C++",
            "town": 4,
        },
        {
            "keyword": "C#",
            "town": 4,
        },
        {
            "keyword": "Ruby",
            "town": 4,
        },
        {
            "keyword": "Go",
            "town": 4,
        },
    ]
    sj_result = {}
    for payload in superjob_payloads:
        superjob_response = requests.get(sj_url, headers=headers, params=payload)
        response_payload = superjob_response.json()

        count = 0
        salary_sum = 0
        page = 1
        sj_result_page = []
        sj_result_page.append(response_payload)
        while response_payload["more"]:
            sj_page_response = requests.get(superjob_response.url, headers=headers, params={"page": page})
            sj_page_payload = sj_page_response.json()
            print(sj_page_response.url)
            sj_result_page.append(sj_page_payload)
            page += 1

        for page in sj_result_page:
            for vacancy in page["objects"]:
                if predict_rub_salary_for_superJob(vacancy) is not None:
                    count += 1
                    salary_sum += predict_rub_salary_for_superJob(vacancy)
            try:
                average_salary = int(salary_sum/count)
            except ZeroDivisionError:
                average_salary = 0

            new_data = {
                payload["keyword"]: {
                    "vacancies_found": response_payload["total"],
                    "vacancies_processed": count,
                    "average_salary": average_salary,
                }
            }
            sj_result.update(new_data)
    return sj_result


def main():
    token = decouple.config('SUPER_JOB_TOKEN')
    superjob_payload = get_vacancies_for_superjob(token)
    draw_table(superjob_payload, "SuperJob Moscow")

    print()
    hh_payload = get_vacancies_for_hh()
    draw_table(hh_payload, "HeadHunter Moscow")


if __name__ == '__main__':
    main()

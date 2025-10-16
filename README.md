# Сравниваем вакансии программистов

Утилита для сравнения вакансий программистов на агрегаторах Headhunter и Superjob

### Как установить

Проект был создан на Python 3.13.2
```
pip install -r requirements.txt
```

### Настройка

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` рядом с `main.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.
* `SUPER_JOB_TOKEN` - Секретный ключ вашего приложения на сайте [Superjob](https://api.superjob.ru/)

### Использование

В проекте есть несколько основных функций:
* `get_vacancies_for_hh` - Возвращает словарь со средними зарплатами и количеством вакансий на сайте HH.
* `get_vacancies_for_superjob` - Возвращает словарь со средними зарплатами и количеством вакансий на сайте Superjob. Требует на вход секретный ключ вашего приложения на сайте [Superjob](https://api.superjob.ru/).

  ```python
  {
  "Python": {
    "vacancies_found": 4711,
    "vacancies_processed": 511,
    "average_salary": 204332
  },
  "Java": {
    "vacancies_found": 1338,
    "vacancies_processed": 239,
    "average_salary": 202564
  },
  "Javascript": {
    "vacancies_found": 1563,
    "vacancies_processed": 538,
    "average_salary": 188798
  },
  "C++": {
    "vacancies_found": 1084,
    "vacancies_processed": 286,
    "average_salary": 203566

  }
  ```
* `draw_table` - Рисует таблицу со средними зарплатами и количеством вакансий. Требует на вход название таблицы и словарь из элементов с вложенными ключами `vacancies_found`, `vacancies_processed`, `average_salary`.
```python
payload = {
            "element": {
              "vacancies_found": vacancies_found,
              "vacancies_processed": vacancies_processed,
              "average_salary": average_salary,
                }
            }
draw_table(payload, "new table")
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

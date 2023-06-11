import json
import requests
import base64
from hashlib import md5
import aiohttp

ege_captcha_url = "https://checkege.rustest.ru/api/captcha"
ege_login_url = "https://checkege.rustest.ru/api/participant/login"
ege_main = "https://checkege.rustest.ru/api/exam"
headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru,ru-RU;q=0.9,en;q=0.8,sr;q=0.7',
    'Connection': 'keep-alive',
    'Cookie': '',
    'DNT': '1',
    'Referer': 'https://checkege.rustest.ru/exams',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 YaBrowser/22.8.0.223 (lite) Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def parse_result(y):
    # print(y['Result']['Exams'])
    answer = ''
    for i in y['Result']['Exams']:
        if answer != '':
            answer += '\n'
        message = ''
        sub_id = i['ExamId']
        subject = 'Экзамен: ' + str(i['Subject'])
        checked = i['HasResult']
        sep = ' | '
        if checked:
            checked = 'Проверен'
        else:
            checked = 'Не проверен'
        mark = 'Балл: ' + str(i["TestMark"])
        if sub_id == 178:
            message = subject + sep + checked
            if checked == 'Проверен':
                if i["TestMark"] == 1:
                    message += sep + 'Зачет'
                else:
                    message += sep + 'Незачет'
        else:
            message = subject + str(sep) + str(checked)
            if checked == 'Проверен':
                message += sep + mark
        answer += message
    return answer

def get_captcha():
    resp = requests.get(url=ege_captcha_url, verify=False)
    data = resp.json()
    image = data['Image']
    token = data['Token']
    with open("captcha/captcha.jpg", "wb") as f:
            f.write(base64.b64decode(image))
    return token


def get_results_from_site(user, captcha_token, captcha_answer):
    headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru,ru-RU;q=0.9,en;q=0.8,sr;q=0.7',
    'Connection': 'keep-alive',
    'Cookie': '',
    'DNT': '1',
    'Referer': 'https://checkege.rustest.ru/exams',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.1.0; Redmi 5 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 YaBrowser/22.8.0.223 (lite) Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
    }
    name = str(user["Name"])
    region = int(user["Region"])
    passport = str(user["Passport"]).rjust(12, '0')
    a = name.split(" ")
    name_merged = md5(''.join(a).lower().replace("ё", "е").replace("й", "и").replace("-", "").encode()).hexdigest()
    name = name_merged
    print(name, region, passport)
    params = {
                "Hash": name,
                "Document": passport,
                "Region": region,
                "Captcha": captcha_answer,
                "Token": captcha_token
            }
    session = requests.Session()
    response = session.post(ege_login_url, data=params, timeout=10, verify=False)
    if "Participant" in response.cookies:
            token = response.cookies["Participant"]
    headerss = headers.copy()
    headerss["Cookie"] += "Participant=" + token
    session = requests.Session()
    response = session.get(ege_main, headers=headerss, timeout=10, verify=False)
    json = response.json()
    # print(json['Result']['Exams'])
    return parse_result(json)
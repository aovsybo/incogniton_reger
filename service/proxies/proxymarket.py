from datetime import datetime, timedelta
import requests

from config import settings
from service.errors import AccountProcessingError


MISTAKE_CODES = {
    "LOW_BALANCE": "Недостаточно средств на балансе proxymarket",
}


def buy_and_get_ips(amount_of_accounts: int):
    """Покупка прокси и возврат ip-адресов"""
    # bought_status = buy_ips(amount_of_accounts)
    # if not bought_status["is_bought"]:
    #     raise AccountProcessingError(MISTAKE_CODES[bought_status["mistake_code"]])
    ip_addresses = get_ip_addresses()
    if not ip_addresses:
        raise AccountProcessingError("Не удалось купить прокси")
    return ip_addresses


def buy_ips(amount_of_accounts: int) -> dict:
    """Покупа указанного количества прокси"""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "PurchaseBilling": {
            "count": amount_of_accounts,
            "type": 100,
            "duration": 30,
            "country": "ru",
            "promocode": "",
            "subnet": "",
            "speed": 3,
        }
    }
    if not settings.PROXY_MARKET_API_TOKEN:
        raise AccountProcessingError("Необходимо ввести токен Proxy.market")
    response = requests.post(
        f'{settings.PROXIES_URL}buy-proxy/{settings.PROXY_MARKET_API_TOKEN}',
        headers=headers,
        json=data
    ).json()
    print(response)
    mistake_code: str = ""
    is_bought: bool = False
    if "success" in response:
        is_bought = response["success"]
        if "code" in response:
            mistake_code = response["code"]
    bought_status = {
        "is_bought": is_bought,
        "mistake_code": mistake_code,
    }
    return bought_status


def is_date_on_timeout(
        str_date: str,
        timeout_minutes: int = settings.PROXY_TIMEOUT_MINUTES,
) -> bool:
    """Проверяет актуальность последних прокси.
    Если с даты покупки последних прокси прошло более 2 минут,
    то это не те прокси, которые были куплены"""
    converted_date = datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()
    return current_date - converted_date <= timedelta(minutes=timeout_minutes)


def get_ip_addresses() -> list[str]:
    """Возвращает информацию о последних купленных прокси"""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = {
        "type": "ipv4",
        "page": 1,
        "page_size": 0,
        "sort": 0,
    }
    response = requests.post(
        f'{settings.PROXIES_URL}list/{settings.PROXY_MARKET_API_TOKEN}',
        headers=headers,
        json=data,
    ).json()
    if "message" in response and response["message"] == 'Неверный api_key':
        raise AccountProcessingError("Неверно введен API-токен")
    list_of_ip_info = response["list"]["data"]
    check_if_ip_enter_data_in_config(list_of_ip_info)
    data_of_last_buying = list_of_ip_info[-1]['bought_at']
    list_of_latest_ip_info = [
        ip_info for ip_info in list_of_ip_info
        if ip_info['bought_at'] == data_of_last_buying
    ]
    # if not is_date_on_timeout(data_of_last_buying):
    #     raise AccountProcessingError("Проблемы с получением прокси")
    proxies = [profile['ip']
               for profile in
               list_of_latest_ip_info[-len(list_of_latest_ip_info)::1]]
    return proxies


def check_if_ip_enter_data_in_config(list_of_ip_info):
    """Проверяет корректность данных в конфиге,
    отвечающих за подключение к прокси"""
    port = f'{settings.PROXY_TYPE}_port'
    if settings.PROXY_LOGIN != list_of_ip_info[-1]['login'] \
            or settings.PROXY_PASSWORD != list_of_ip_info[-1]['password'] \
            or settings.PROXY_PORT != list_of_ip_info[-1][port]:
        settings.update_config_data(
            PROXY_LOGIN=list_of_ip_info[-1]['login'],
            PROXY_PASSWORD=list_of_ip_info[-1]['password'],
            PROXY_PORT=list_of_ip_info[-1][f'{settings.PROXY_TYPE}_port']
        )

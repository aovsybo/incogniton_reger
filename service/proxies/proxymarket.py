from datetime import datetime, timedelta
import requests

from config import settings
from service.errors import AccountProcessingError


def buy_and_get_ips(amount_of_accounts: int):
    """Возврат последних купленных ip-адресов"""
    list_of_ip_info = get_ip_info()
    check_ip_enter_data(list_of_ip_info)
    ip_addresses = [profile["ip"] for profile in
                    list_of_ip_info[-len(list_of_ip_info)::1]]
    return ip_addresses


# def buy_and_get_ips(amount_of_accounts: int):
#    """Покупка прокси и возврат ip-адресов"""
#     if not buy_ips(amount_of_accounts):
#         raise AccountProcessingError("Необходимо пополнить баланс")
#     list_of_ip_info = get_ip_info()
#     check_ip_enter_data(list_of_ip_info)
#     ip_addresses = get_ip_addresses(list_of_ip_info)
#     return ip_addresses


def buy_ips(amount_of_accounts: int) -> bool:
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
    )
    return response.json()["success"]


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


def get_ip_info() -> list[str]:
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
    list_of_ip_info = requests.post(
        f'{settings.PROXIES_URL}list/{settings.PROXY_MARKET_API_TOKEN}',
        headers=headers,
        json=data,
    ).json()['list']['data']

    list_of_latest_ip_info = [
        ip_info for ip_info in list_of_ip_info
        if ip_info['bought_at'] == list_of_ip_info[-1]['bought_at']
    ]
    return list_of_latest_ip_info


def check_ip_enter_data(list_of_ip_info):
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


def get_ip_addresses(list_of_ip_info) -> list[str]:
    """Возвращает список ip-адресов последних купленных прокси"""
    if not is_date_on_timeout(list_of_ip_info[-1]['bought_at']):
        raise AccountProcessingError("Проблемы с получением прокси")
    proxies = [profile['ip']
               for profile in
               list_of_ip_info[-len(list_of_ip_info)::1]]
    return proxies

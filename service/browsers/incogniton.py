import requests

from model import CreateIncognitonAccountInfo
from config import settings


# TODO: Возвращать количество созданных акков
def create_accounts(ip_addresses: list[str]) -> int:
    """Создание профилей Incogniton с указанными прокси-адресами"""
    responses = []
    for index, ip_address in enumerate(ip_addresses):
        profile_name = settings.BROWSER_NAME_PREFIX + \
                       str(settings.BROWSER_NAME_SHIFT + index)
        account_info = CreateIncognitonAccountInfo(
            profile_name=profile_name,
            profile_group=settings.BROWSER_GROUP_NAME,
            proxy_host=ip_address,
            proxy_type=settings.PROXY_TYPE,
            proxy_port=settings.PROXY_PORT,
            proxy_login=settings.PROXY_LOGIN,
            proxy_password=settings.PROXY_PASSWORD,
        )
        responses.append(requests.post(
            url=f"{settings.INCOGNITON_URL}add",
            data={'profileData': account_info.get_request()}
        ))
    amount_of_created_accounts = len(responses)
    return amount_of_created_accounts

import requests

from config import settings
from model import CreateDolphinAccountInfo
from service.errors import AccountProcessingError


# TODO: Допилить уникализацию настроек webgl info
def create_accounts(ip_addresses: list[str]) -> int:
    """Создание профилей Dolphin с указанными прокси-адресами"""
    if not settings.DOLPHIN_API_TOKEN:
        raise AccountProcessingError("Необходимо ввести токен Dolphin")
    request_headers = {
        "Authorization": f"Bearer {settings.DOLPHIN_API_TOKEN}",
        "Content-Type": "application/json",
    }
    responses = []
    for i, ip_address in enumerate(ip_addresses):
        number_of_account = str(settings.BROWSER_NAME_SHIFT + i)
        proxy_type = "socks5" if settings.PROXY_TYPE == "socks" else "http"
        account_info = CreateDolphinAccountInfo(
            profile_name=settings.BROWSER_NAME_PREFIX + number_of_account,
            profile_group=settings.BROWSER_GROUP_NAME,
            proxy_host=ip_address,
            proxy_type=proxy_type,
            proxy_port=settings.PROXY_PORT,
            proxy_login=settings.PROXY_LOGIN,
            proxy_password=settings.PROXY_PASSWORD,
        )
        responses.append(requests.post(
            url=f"{settings.REMOTE_DOLPHIN_URL}browser_profiles",
            headers=request_headers,
            data=account_info.get_request(),
        ))
    amount_of_created_accounts = len([account for account in responses if account.json()["success"]])
    return amount_of_created_accounts

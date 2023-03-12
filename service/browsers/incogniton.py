import requests

from model import CreateIncognitonAccountInfo
from config import settings


MISTAKE_LIMIT_PROFILES = 'CREATING PROFILE: Your subscription has not enough space for more profiles.'
MISTAKE_GROUP_NAME_DOESNT_EXIST = 'Cannot invoke "com.incogniton.logic.group.model.Group.getName()" ' \
                                  'because the return value of "com.incogniton.logic.profile.model' \
                                  '.generalInformation.GeneralInformation.getGroup()" is null'

MISTAKES = {
    MISTAKE_LIMIT_PROFILES: "Превышен лимит создания аккаунтов.",
    MISTAKE_GROUP_NAME_DOESNT_EXIST: "Отстутствует группа с указанным именем.",
}


def create_accounts(ip_addresses: list[str]) -> dict:
    """Создание профилей Incogniton с указанными прокси-адресами"""
    responses = []
    for index, ip_address in enumerate(ip_addresses):
        name_prefix = settings.BROWSER_NAME_PREFIX if settings.BROWSER_NAME_PREFIX else ""
        profile_name = name_prefix + str(settings.BROWSER_NAME_SHIFT + index)
        profile_group = settings.BROWSER_GROUP_NAME if settings.BROWSER_GROUP_NAME else "Unassigned"
        proxy_type = "SOCKS 5" if settings.PROXY_TYPE == "socks" else "HTTP"
        account_info = CreateIncognitonAccountInfo(
            profile_name=profile_name,
            profile_group=profile_group,
            proxy_host=ip_address,
            proxy_type=f"{proxy_type} proxy",
            proxy_port=settings.PROXY_PORT,
            proxy_login=settings.PROXY_LOGIN,
            proxy_password=settings.PROXY_PASSWORD,
        )
        responses.append(requests.post(
            url=f"{settings.INCOGNITON_URL}add",
            data={'profileData': account_info.get_request()},
        ).json())
    mistake_message: str = ""
    amount_of_created_accounts: int = 0
    for response in responses:
        if "status" in response:
            if response["status"] == "error" and "message" in response:
                mistake_message = MISTAKES.get(response["message"], "Неизвестная ошибка.")
            if response["status"] == "ok":
                amount_of_created_accounts += 1
    status_of_creating = {
        "amount_of_created_accounts": amount_of_created_accounts,
        "mistake_message": mistake_message,
    }
    return status_of_creating

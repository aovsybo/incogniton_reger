from itertools import chain
from typing import Protocol, Sequence

from src.config import settings
from src.model import RegerSettings
from src.service.errors import AccountProcessingError

from src.service.proxies import proxymarket
from src.service.browsers import incogniton


class InterfaceField(Protocol):
    def get(self) -> str: ...

    def mark_errored(self) -> None: ...

    def unmark_errored(self) -> None: ...


def save_settings_to_config(
        interface_setting_fields: Sequence[InterfaceField],
        settings_input_error_label_text,
):
    """Сохранение настроек из полей ввода view.py в config.py"""
    try:
        config = RegerSettings(**{
            name: interface_setting_fields[index].get()
            for index, name in
            enumerate(RegerSettings.__fields__)
        })
    except ValueError as e:
        error_fields = tuple(chain.from_iterable(
            err["loc"] for err in e.errors())
        )
        for index, name in enumerate(RegerSettings.__fields__):
            if name in error_fields:
                settings_input_error_label_text.set(
                    f"Необходимо ввести значение в поле '{RegerSettings.ru(name)}'"
                )
    else:
        settings_input_error_label_text.set("")
        settings.update_config_data(**dict(config))


def create_accounts(entry_for_amount_of_accounts, feedback_text):
    """Покупка прокси и создание аккаунтов в браузере"""
    try:
        amount_of_accounts = int(entry_for_amount_of_accounts.get())
    except ValueError as e:
        raise AccountProcessingError("Необходимо укзаать положительное число")
    if amount_of_accounts <= 0:
        raise AccountProcessingError("Необходимо укзаать положительное число")

    settings.update_config_data(
        PREVIOUS_NUMBER_OF_PURCHASED_ACCOUNTS=amount_of_accounts
    )
    proxy_ip_addresses = proxymarket.buy_and_get_ips(amount_of_accounts)
    status_of_creating = incogniton.create_accounts(proxy_ip_addresses)
    if status_of_creating["amount_of_created_accounts"] == amount_of_accounts:
        feedback_text.set(f"Создано аккаунтов: {status_of_creating['amount_of_created_accounts']}")
    else:
        feedback_text.set(f"{status_of_creating['mistake_message']} "
                          f"Создано аккаунтов: {status_of_creating['amount_of_created_accounts']}")
    settings.update_config_data(
        BROWSER_NAME_SHIFT=settings.BROWSER_NAME_SHIFT+status_of_creating['amount_of_created_accounts']
    )


def choose_proxy_type(proxy_type):
    """Обновление поля "PROXY_TYPE" в конфиге"""
    settings.update_config_data(PROXY_TYPE=proxy_type)

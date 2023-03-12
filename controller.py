from itertools import chain
from typing import Protocol, Sequence

from config import settings
from model import RegerSettings
from service import browsers
from service import proxies
from service.proxies import proxymarket
from service.browsers import incogniton, dolphin


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
                    f"Необходимо ввести числовое значение в поле '{RegerSettings.ru(name)}'"
                )
    else:
        settings_input_error_label_text.set("")
        settings.update_config_data(**dict(config))


def create_accounts(entry_for_amount_of_accounts, feedback_text):
    """Покупка прокси и создание аккаунтов в браузере"""
    amount_of_accounts = int(entry_for_amount_of_accounts.get())
    settings.update_config_data(
        PREVIOUS_NUMBER_OF_PURCHASED_ACCOUNTS=amount_of_accounts
    )
    proxy_ip_addresses = getattr(
        proxies,
        settings.CHOSEN_PROXY_APP
    ).buy_and_get_ips(amount_of_accounts)
    status_of_creating = getattr(
        browsers,
        settings.CHOSEN_BROWSER_APP
    ).create_accounts(proxy_ip_addresses)
    if status_of_creating["amount_of_created_accounts"] == amount_of_accounts:
        feedback_text.set("Аккаунты успешно созданы")
    else:
        feedback_text.set(f"{status_of_creating['mistake_message']} "
                          f"Создано аккаунтов: {status_of_creating['amount_of_created_accounts']}")
    settings.update_config_data(
        BROWSER_NAME_SHIFT=settings.BROWSER_NAME_SHIFT+status_of_creating['amount_of_created_accounts']
    )


def choose_proxy(name):
    """Обновление поля "CHOSEN_PROXY_APP" в конфиге"""
    settings.update_config_data(CHOSEN_PROXY_APP=name)


def choose_browser(name):
    """Обновление поля "CHOSEN_BROWSER_APP" в конфиге"""
    settings.update_config_data(CHOSEN_BROWSER_APP=name)


def choose_proxy_type(proxy_type):
    """Обновление поля "PROXY_TYPE" в конфиге"""
    settings.update_config_data(PROXY_TYPE=proxy_type)

from typing import ClassVar
from pydantic import BaseModel, validator


class RegerSettings(BaseModel):
    """Класс с  полями, выводимыми во вкладке "настройки" во view.py"""
    _ru: ClassVar[dict[str, str]] = {
        "PROXY_MARKET_API_TOKEN": "Токен Прокси",
        "DOLPHIN_API_TOKEN": "Токен Dolphin",
        "BROWSER_NAME_SHIFT": "Сдвиг",
        "BROWSER_NAME_PREFIX": "Префикс имени",
        "BROWSER_GROUP_NAME": "Группа",
    }

    PROXY_MARKET_API_TOKEN: str | None
    DOLPHIN_API_TOKEN: str | None
    BROWSER_NAME_SHIFT: int
    BROWSER_NAME_PREFIX: str | None
    BROWSER_GROUP_NAME: str

    @classmethod
    def ru(cls, field: str):
        try:
            return cls._ru[field]
        except KeyError:
            raise AttributeError(
                f"'{cls.__name__}' class has no attribute '{field}'"
            )

    @validator('DOLPHIN_API_TOKEN')
    def empty_string_dolphin_api_token_convert_to_null(cls, v):
        return None if v == "" else v

    @validator('BROWSER_NAME_PREFIX')
    def empty_string_browser_name_prefix_convert_to_null(cls, v):
        return None if v == "" else v

    @validator('PROXY_MARKET_API_TOKEN')
    def empty_string_proxy_market_api_token_convert_to_null(cls, v):
        return None if v == "" else v


class CreateAccountInfo(BaseModel):
    """Класс с полями для создания профилей в браузере"""
    info_template: ClassVar[str]
    profile_name: str
    profile_group: str
    proxy_host: str
    proxy_type: str
    proxy_port: str
    proxy_login: str
    proxy_password: str

    def get_request(self):
        raise NotImplementedError


class CreateIncognitonAccountInfo(CreateAccountInfo):
    """Создание тела запроса в Incogniton"""
    info_template = """{{
           "general_profile_information": {{
               "profile_name": "{profile_name}",
               "profile_notes": "",
               "profile_group": "{profile_group}",
               "profile_last_edited": "",
               "simulated_operating_system": "Windows"
           }},
           "Proxy": {{
               "connection_type": "HTTP proxy",
               "proxy_url": "{proxy_url}",
               "proxy_username": "{proxy_login}",
               "proxy_password": "{proxy_password}",
               "proxy_rotating": "0"
           }}
       }}"""

    def get_request(self):
        profile_data = self.info_template.format(
            profile_name=self.profile_name,
            profile_group=self.profile_group,
            proxy_type=f"{self.proxy_type.upper()} proxy",
            proxy_url=f'{self.proxy_host}:{self.proxy_port}',
            proxy_login=self.proxy_login,
            proxy_password=self.proxy_password,
        )
        return profile_data


class CreateDolphinAccountInfo(CreateAccountInfo):
    """Создание тела запроса в Dolphin"""
    info_template = """{{
        "name": "{profile_name}",
        "tags": ["{profile_group}"],
        "platform": "windows",
        "mainWebsite": "",
        "browserType": "anty",
        "useragent": {{
            "mode": "manual",
            "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }},
        "webgl": {{"mode": "real"}},
        "webglInfo": {{"mode": "real"}},
        "cpu": {{"mode": "real"}},
        "memory": {{"mode": "real"}},
        "proxy": {{
            "name": "{proxy_name}",
            "host": "{proxy_host}",
            "port": "{proxy_port}",
            "type": "{proxy_type}",
            "login": "{proxy_login}",
            "password": "{proxy_password}"
        }},
        "mediaDevices": {{
            "mode": "manual",
            "audioInputs": 1,
            "videoInputs": 1,
            "audioOutputs": 2
        }}
    }}"""

    def get_request(self):
        profile_data = self.info_template.format(
            profile_name=self.profile_name,
            profile_group=self.profile_group,
            proxy_name=f"{self.proxy_type}://{self.proxy_host}:{self.proxy_port}:"
                       f"{self.proxy_login}:{self.proxy_password}",
            proxy_host=self.proxy_host,
            proxy_type=self.proxy_type,
            proxy_port=self.proxy_port,
            proxy_login=self.proxy_login,
            proxy_password=self.proxy_password,
        )
        return profile_data.encode('utf-8')

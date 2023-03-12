import json
from pathlib import Path

from pydantic import AnyHttpUrl, BaseSettings, HttpUrl


class Settings(BaseSettings):
    PROJECT_PATH: Path = Path(__file__).parent
    APPSETTINGS_PATH: Path = PROJECT_PATH / "appsettings.json"
    PROXIES_URL: HttpUrl = 'https://proxy.market/dev-api/'
    INCOGNITON_URL: AnyHttpUrl = "http://localhost:35000/profile/"
    PROXY_TIMEOUT_MINUTES: int = 2
    LIST_OF_PROXY_TYPES: list[str] = ["http", "socks"]
    VIEW_WINDOW_PARAMS: dict[str, int] = {"width": 600, "height": 300, "x_shift": 300, "y_shift": 300}
    VIEW_FONT_SIZE: int = 14
    PROXY_MARKET_API_TOKEN: str
    BROWSER_NAME_SHIFT: int
    BROWSER_NAME_PREFIX: str | None
    BROWSER_GROUP_NAME: str | None
    PROXY_LOGIN: str
    PROXY_PASSWORD: str
    PROXY_TYPE: str
    PROXY_PORT: str
    PREVIOUS_NUMBER_OF_PURCHASED_ACCOUNTS: int

    def __init__(self):
        with open(
                self.__class__.__fields__['APPSETTINGS_PATH'].default
        ) as appsettings_file:
            config = json.load(appsettings_file)
        super().__init__(**config)

    def update_config_data(self, **reger_settings):
        with open('appsettings.json', 'r') as file_read:
            config = dict(json.loads(file_read.read()))
        for key, value in reger_settings.items():
            config[key] = value
        with open('appsettings.json', 'w') as file_write:
            json.dump(config, file_write, indent=2)
        for key, value in reger_settings.items():
            setattr(self, key, value)


settings = Settings()

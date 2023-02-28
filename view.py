from functools import partial
from tkinter import *
from tkinter import ttk
from typing import Callable

from config import settings
from controller import save_settings_to_config, \
    create_accounts, choose_proxy, choose_browser, choose_proxy_type
from model import RegerSettings
from service.errors import AccountProcessingError
from utils import aggregate_callables

# TODO: Сделать крупнее шрифты

class HighlightingEntry(Entry):
    """Реализация подсветки неверных данных в полях ввода"""
    def mark_errored(self):
        self.config(
            highlightbackground="red",
            highlightcolor="red",
            highlightthickness=1
        )

    def unmark_errored(self):
        self.config(highlightthickness=0)


class Window(Tk):
    def __init__(self):
        super().__init__()
        self.title("Создание аккаунтов")
        self.geometry("400x200+300+300")
        self.init_menu()

    def init_menu(self):
        """Инициализация вкладок окна"""
        window_tabs = ttk.Notebook()
        window_tabs.pack(fill='both', expand=TRUE)
        frame_names = ["Создание", "Настройки", "Выбор ПО"]
        frames = []
        for i, name in enumerate(frame_names):
            frames.append(ttk.Frame(window_tabs, padding=10))
            frames[i].pack(fill='both', expand=TRUE)
            window_tabs.add(frames[i], text=name)
        self.init_main(frames[0])
        self.init_settings(frames[1])
        self.init_programs(frames[2])

    def init_main(self, frame):
        """Инициализация вкладки создания аккаунтов"""
        info_label = Label(frame, text="Укажите количество аккаунтов: ")
        info_label.grid(column=0, row=0, sticky=E)
        entry_for_amount_of_accounts = Entry(frame)
        entry_for_amount_of_accounts.grid(column=1, row=0)
        entry_for_amount_of_accounts.insert(
            0,
            settings.PREVIOUS_NUMBER_OF_PURCHASED_ACCOUNTS
        )
        entry_for_amount_of_accounts.focus()
        create_button = Button(
            frame,
            text="Создать",
            command=partial(
                aggregate_callables,
                partial(create_accounts, entry_for_amount_of_accounts=entry_for_amount_of_accounts),
                self.update_shift_field
            )
        )
        create_button.grid(column=2, row=0, sticky=E, padx=5)
        self.mistakes_text = StringVar()
        mistakes_label = Label(frame, textvariable=self.mistakes_text)
        mistakes_label.grid(column=1, row=2, sticky=E)

    def init_settings(self, frame) -> None:
        """Инициализация вкладки с настройками"""
        self.config_entries = []
        self.config_labels = []
        for index, field in enumerate(RegerSettings.__fields__):
            self.config_labels.append(Label(
                frame,
                text=RegerSettings.ru(field),
                width=11,
                anchor=E
            ))
            self.config_labels[index].grid(column=0, row=index, padx=3, pady=2)
            self.config_entries.append(HighlightingEntry(frame, width=47))
            self.config_entries[index].grid(column=1, row=index, pady=2)
            default_field_value = getattr(settings, field) \
                if getattr(settings, field) is not None else ""
            self.config_entries[index].insert(0, default_field_value)
        self.toggle_input()
        self.proxy_type_choice = StringVar()
        self.create_radio_buttons(
            frame,
            settings.PROXY_TYPE,
            settings.LIST_OF_PROXY_TYPES.keys(),
            choose_proxy_type,
            self.update_shift_field,
            len(RegerSettings.__fields__) + 1,
            self.proxy_type_choice
        )
        save_button = Button(
            frame,
            text="Сохранить",
            command=partial(
                save_settings_to_config,
                interface_setting_fields=self.config_entries
            ),
        )
        save_button.grid(
            column=1,
            row=len(RegerSettings.__fields__) + 3,
            sticky=S + E,
            pady=5
        )

    def create_radio_buttons(
            self,
            frame,
            chosen_app: str,
            list_of_chosen_apps: list[str],
            update_command: Callable[[str], None],
            switch_command: Callable[[str], None],
            row: int,
            choice: StringVar
    ) -> None:
        choice.set(chosen_app)
        for i, app_name in enumerate(list_of_chosen_apps):
            radio_button = Radiobutton(
                frame,
                text=app_name.capitalize(),
                variable=choice,
                value=app_name,
                command=partial(
                    aggregate_callables,
                    partial(update_command, app_name),
                    switch_command
                ),
            )
            radio_button.grid(column=i, row=row)

    def init_programs(self, frame) -> None:
        """Инициализация вкладки с выбором программ"""
        self.proxy_choice = StringVar()
        self.browser_choice = StringVar()
        self.create_radio_buttons(
            frame,
            settings.CHOSEN_BROWSER_APP,
            settings.LIST_OF_BROWSER_APPS,
            choose_browser,
            self.toggle_input,
            0,
            self.proxy_choice
        )
        self.create_radio_buttons(
            frame,
            settings.CHOSEN_PROXY_APP,
            settings.LIST_OF_PROXY_APPS,
            choose_proxy,
            self.toggle_input,
            1,
            self.browser_choice
        )

    def toggle_input(self) -> None:
        """Включение и выключение отображения поля ввода токена Dolphin"""
        for i, entry in enumerate(self.config_entries):
            if (self.config_labels[i]["text"] == "Токен Dolphin") and \
                    (settings.CHOSEN_BROWSER_APP != "Dolphin"):
                self.config_labels[i].grid_forget()
                entry.grid_forget()
            elif (self.config_labels[i]["text"] == "Токен Dolphin") and \
                    (settings.CHOSEN_BROWSER_APP == "Dolphin"):
                entry.grid(column=1, row=1)
                self.config_labels[i].grid(column=0, row=1)

    def update_shift_field(self) -> None:
        """Актуализация данных поля "Сдвиг" после создания аккаунтов"""
        for i, entry in enumerate(self.config_entries):
            if self.config_labels[i]["text"] == "Сдвиг":
                entry.delete(0, END)
                entry.insert(0, settings.BROWSER_NAME_SHIFT)

    def report_callback_exception(self, exc, val, tb) -> None:
        if exc is AccountProcessingError:
            self.mistakes_text.set(val)


def mainloop():
    app = Window()
    app.mainloop()

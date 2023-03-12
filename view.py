from functools import partial

import customtkinter as ct
from tkinter import *
from typing import Callable

from config import settings
from controller import save_settings_to_config, create_accounts, choose_proxy_type
from model import RegerSettings
from service.errors import AccountProcessingError
from utils import aggregate_callables


class Window(ct.CTk):
    def __init__(self):
        super().__init__()
        self.title("Создание профилей")
        self.geometry(f"{settings.VIEW_WINDOW_PARAMS['width']}x"
                      f"{settings.VIEW_WINDOW_PARAMS['height']}+"
                      f"{settings.VIEW_WINDOW_PARAMS['x_shift']}+"
                      f"{settings.VIEW_WINDOW_PARAMS['y_shift']}")
        self.resizable(False, False)
        self.bind_all("<Key>", self._on_key_release, "+")
        ct.set_appearance_mode("light")
        self.init_menu()

    def _on_key_release(self, event):
        """Позволяет копировать, вставлять и вырезать при русской раскладке"""
        ctrl = (event.state & 0x4) != 0
        if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
            event.widget.event_generate("<<Cut>>")

        if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
            event.widget.event_generate("<<Paste>>")

        if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
            event.widget.event_generate("<<Copy>>")

        if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
            event.widget.event_generate("<<SelectAll>>")


    def init_menu(self):
        """Инициализация вкладок окна"""
        window_tabview = ct.CTkTabview(self)
        window_tabview.pack(fill='both', expand=TRUE)
        frame_names = ["Создание", "Настройки"]
        for name in frame_names:
            window_tabview.add(name)
            window_tabview.tab(name).grid_columnconfigure(0)
        self.init_main(window_tabview.tab(frame_names[0]))
        self.init_settings(window_tabview.tab(frame_names[1]))

    def init_main(self, frame):
        """Инициализация вкладки создания аккаунтов"""
        info_label = ct.CTkLabel(
            frame,
            text="Укажите количество аккаунтов:",
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
            anchor="center",
        )
        info_label.grid(column=0, row=0, padx=(20, 0), pady=20)
        entry_for_amount_of_accounts = ct.CTkEntry(
            frame,
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
            width=180,
        )
        entry_for_amount_of_accounts.grid(column=1, row=0, padx=10)
        entry_for_amount_of_accounts.insert(
            0,
            settings.PREVIOUS_NUMBER_OF_PURCHASED_ACCOUNTS
        )
        self.feedback_text = StringVar()
        feedback_label = ct.CTkLabel(
            frame,
            textvariable=self.feedback_text,
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
        )
        feedback_label.grid(column=0, columnspan=3, row=2)
        create_button = ct.CTkButton(
            frame,
            text="Создать",
            command=partial(
                aggregate_callables,
                partial(
                    create_accounts,
                    entry_for_amount_of_accounts=entry_for_amount_of_accounts,
                    feedback_text=self.feedback_text,
                ),
                self.update_shift_field,
            )
        )
        create_button.grid(column=2, row=0)

    def create_settings_line(self, frame, field, index):
        self.config_labels.append(ct.CTkLabel(
            frame,
            text=RegerSettings.ru(field),
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
        ))
        self.config_labels[index].grid(column=0, row=index, padx=(110, 5), pady=2, sticky="E")
        self.config_entries.append(ct.CTkEntry(
            frame,
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
            width=240
        ))
        self.config_entries[index].grid(column=1, row=index, columnspan=2, pady=2, sticky="W")
        default_field_value = getattr(settings, field) \
            if getattr(settings, field) is not None else ""
        self.config_entries[index].insert(0, default_field_value)

    def init_settings(self, frame) -> None:
        """Инициализация вкладки с настройками"""
        self.config_entries = []
        self.config_labels = []
        for index, field in enumerate(RegerSettings.__fields__):
            self.create_settings_line(frame, field, index)
        ct.CTkLabel(
            frame,
            text="Тип прокси",
            anchor=E,
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
        ).grid(column=0, row=len(RegerSettings.__fields__) + 1, padx=(110, 5), pady=2, sticky="E")
        self.proxy_type_choice = StringVar()
        self.create_radio_buttons(
            frame,
            settings.PROXY_TYPE,
            settings.LIST_OF_PROXY_TYPES,
            choose_proxy_type,
            self.update_shift_field,
            len(RegerSettings.__fields__) + 1,
            self.proxy_type_choice
        )
        self.settings_input_error_label_text = StringVar()
        save_button = ct.CTkButton(
            frame,
            text="Сохранить",
            command=partial(
                save_settings_to_config,
                interface_setting_fields=self.config_entries,
                settings_input_error_label_text = self.settings_input_error_label_text
            ),
        )
        save_button.grid(
            column=2,
            row=len(RegerSettings.__fields__) + 3,
            sticky=S + E,
            pady=5
        )
        settings_input_error_label = ct.CTkLabel(
            frame,
            textvariable=self.settings_input_error_label_text,
            font=ct.CTkFont(size=settings.VIEW_FONT_SIZE),
        )
        settings_input_error_label.grid(
            column=0,
            columnspan=3,
            row=len(RegerSettings.__fields__) + 4,
            padx=(70, 0),
            pady=(10, 0)
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
            radio_button = ct.CTkRadioButton(
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
            radio_button.grid(column=i+1, row=row, padx=(30, 0), pady=2)

    def update_shift_field(self) -> None:
        """Актуализация данных поля "Сдвиг" после создания аккаунтов"""
        searching_value = RegerSettings.ru("BROWSER_NAME_SHIFT")
        for i, entry in enumerate(self.config_entries):
            if self.config_labels[i]._text == searching_value:
                entry.delete(0, END)
                entry.insert(0, settings.BROWSER_NAME_SHIFT)

    def report_callback_exception(self, exc, val, tb) -> None:
        if exc is AccountProcessingError:
            self.feedback_text.set(val)


def mainloop():
    app = Window()
    app.mainloop()

"""
Страница входа ЭЖКСР.
Работает как фрейм внутри MainApp.
"""

import customtkinter as ctk
from tkinter import messagebox


BG_COLOR = "#1E3A8A"
CARD_BG = "#FFFFFF"
TITLE_COLOR = "#1E3A8A"
TEXT_GRAY = "#252A30"
LABEL_COLOR = "#334155"
INPUT_BG = "#F8FAFC"
INPUT_BORDER = "#CBD5E1"
BTN_BG = "#2563EB"
BTN_HOVER = "#1D4ED8"
LINK_COLOR = "#2563EB"


class LoginPage(ctk.CTkFrame):
    """Фрейм входа."""

    def __init__(self, parent, on_success, on_register):
        """
        Конструктор.

        Args:
            parent: родитель (MainApp)
            on_success: функция при успешном входе
            on_register: функция перехода на регистрацию
        """
        super().__init__(parent, fg_color=BG_COLOR)

        self.on_success = on_success
        self.on_register = on_register

        # Центральная карточка
        card = ctk.CTkFrame(self, width=420, height=500,
                            corner_radius=16, fg_color=CARD_BG)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)


        ctk.CTkLabel(card, text="ЭЖКСР",
                     font=("Inter", 22, "bold"),
                     text_color=TITLE_COLOR).pack()

        ctk.CTkLabel(card,
                     text="Электронный журнал кружковой\nи секционной работы",
                     font=("Inter", 12),
                     text_color=TEXT_GRAY,
                     justify="center").pack(pady=(4, 24))

        # Роль
        ctk.CTkLabel(card, text="Роль",
                     font=("Inter", 13, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", padx=36)

        self.role_var = ctk.StringVar(value="Преподаватель")
        ctk.CTkOptionMenu(
            card,
            values=["Преподаватель", "Студент", "Администратор"],
            variable=self.role_var,
            fg_color=INPUT_BG,
            button_color=INPUT_BORDER,
            text_color="#1E293B",
            font=("Inter", 14),
            height=45, corner_radius=8
        ).pack(fill="x", padx=36, pady=(6, 18))

        # Логин
        ctk.CTkLabel(card, text="Логин",
                     font=("Inter", 13, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", padx=36)

        self.login_entry = ctk.CTkEntry(
            card, placeholder_text="введите логин",
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            text_color="#111010",
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.login_entry.pack(fill="x", padx=36, pady=(6, 18))

        # Пароль
        ctk.CTkLabel(card, text="Пароль",
                     font=("Inter", 13, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", padx=36)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="введите пароль",
            show="•",
            text_color="#111010",
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.password_entry.pack(fill="x", padx=36, pady=(6, 24))

        # Кнопка «Войти»
        ctk.CTkButton(
            card, text="Войти в систему",
            font=("Inter", 14, "bold"),
            fg_color=BTN_BG, hover_color=BTN_HOVER,
            height=45, corner_radius=8,
            command=self.on_login
        ).pack(fill="x", padx=36)

        # Ссылка «Регистрация»
        link = ctk.CTkLabel(
            card,
            text="Нет аккаунта? Зарегистрироваться",
            font=("Inter", 12),
            text_color=LINK_COLOR,
            cursor="hand2"
        )
        link.pack(pady=(16, 40))
        link.bind("<Button-1>", lambda e: self.on_register())

    def on_login(self):
        """Обработка входа."""
        from logic.auth import authenticate

        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните логин и пароль")
            return

        user = authenticate(login, password)

        if user is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        # Вызываем callback — передаём пользователя
        self.on_success(user)
"""
Экран регистрации ЭЖКСР.
Соответствует макету: Рисунок 3 — Форма регистрации программы.
"""

import customtkinter as ctk
from tkinter import messagebox


class RegisterWindow(ctk.CTk):
    """Окно регистрации нового пользователя."""

    def __init__(self):
        super().__init__()

        # --- Настройки окна ---
        self.title("ЭЖКСР — Регистрация")
        self.geometry("1440x1024")
        self.resizable(False, False)
        self.configure(fg_color="#1E3A8A")

        # --- Центральная карточка ---
        self.card = ctk.CTkFrame(
            self,
            width=560,
            height=520,
            corner_radius=16,
            fg_color="#FFFFFF"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # --- Заголовок ---
        ctk.CTkLabel(
            self.card,
            text="ЭЖКСР — Регистрация",
            font=("Inter", 20, "bold"),
            text_color="#1E3A8A"
        ).pack(pady=(36, 6))

        ctk.CTkLabel(
            self.card,
            text="Заполните данные для создания аккаунта",
            font=("Inter", 12),
            text_color="#64748B"
        ).pack(pady=(0, 24))

        # --- Контейнер для двух колонок ---
        self.form = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form.pack(fill="x", padx=36)

        # --- Левая колонка ---
        left = ctk.CTkFrame(self.form, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        self._add_field(left, "ФИО", "введите ФИО")
        self._add_field(left, "Логин", "введите логин")
        self._add_field(left, "Пароль", "введите пароль", show="•")
        self._add_field(left, "Подтверждение пароля", "повторите пароль", show="•")

        # --- Правая колонка ---
        right = ctk.CTkFrame(self.form, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self._add_field(right, "Email", "введите email")
        self._add_field(right, "Телефон", "введите телефон")
        self._add_role_field(right)
        self._add_group_field(right)

        # --- Кнопки ---
        buttons = ctk.CTkFrame(self.card, fg_color="transparent")
        buttons.pack(fill="x", padx=36, pady=(24, 36))

        ctk.CTkButton(
            buttons,
            text="Отмена",
            font=("Inter", 14, "bold"),
            fg_color="transparent",
            border_width=2,
            border_color="#CBD5E1",
            text_color="#475569",
            hover_color="#F1F5F9",
            height=45,
            corner_radius=8,
            command=self.on_cancel
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            buttons,
            text="Зарегистрироваться",
            font=("Inter", 14, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=45,
            corner_radius=8,
            command=self.on_register
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def _add_field(self, parent, label_text, placeholder, show=None):
        """Добавить поле ввода с подписью."""
        ctk.CTkLabel(
            parent,
            text=label_text,
            font=("Inter", 12, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            show=show if show else "",
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13),
            height=40,
            corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 14))
        return entry

    def _add_role_field(self, parent):
        """Добавить селект роли."""
        ctk.CTkLabel(
            parent,
            text="Роль",
            font=("Inter", 12, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        self.role_var = ctk.StringVar(value="Студент")
        ctk.CTkOptionMenu(
            parent,
            values=["Студент", "Преподаватель"],
            variable=self.role_var,
            fg_color="#F8FAFC",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=40,
            corner_radius=8
        ).pack(fill="x", pady=(0, 14))

    def _add_group_field(self, parent):
        """Добавить поле группы."""
        ctk.CTkLabel(
            parent,
            text="Группа",
            font=("Inter", 12, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkEntry(
            parent,
            placeholder_text="ИСП-34",
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13),
            height=40,
            corner_radius=8
        ).pack(fill="x", pady=(0, 14))

    def on_register(self):
        """Обработка нажатия «Зарегистрироваться»."""
        messagebox.showinfo("Успех", "Регистрация выполнена!")

    def on_cancel(self):
        """Вернуться к окну входа."""
        from ui.login import LoginWindow
        self.destroy()
        app = LoginWindow()
        app.mainloop()


if __name__ == "__main__":
    app = RegisterWindow()
    app.mainloop()
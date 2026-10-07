"""
Страница регистрации ЭЖКСР.
Работает как фрейм внутри MainApp.
"""

import customtkinter as ctk
from tkinter import messagebox


BG_COLOR = "#1E3A8A"
CARD_BG = "#FFFFFF"
TITLE_COLOR = "#1E3A8A"
LABEL_COLOR = "#202122"
INPUT_BG = "#F8FAFC"
INPUT_BORDER = "#CBD5E1"

TAB_ACTIVE_BG = "#2563EB"
TAB_ACTIVE_TEXT = "#FFFFFF"
TAB_INACTIVE_BG = "transparent"
TAB_INACTIVE_TEXT = "#475569"
TAB_INACTIVE_BORDER = "#CBD5E1"
TAB_HOVER = "#1D4ED8"


class RegisterPage(ctk.CTkFrame):
    """Фрейм регистрации."""

    def __init__(self, parent, on_success, on_cancel):
        super().__init__(parent, fg_color=BG_COLOR)

        self.on_success = on_success
        self.on_cancel = on_cancel

        # Карточка
        self.card = ctk.CTkFrame(self, width=900, height=560,
                                 corner_radius=16, fg_color=CARD_BG)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)

        # Заголовок
        header = ctk.CTkFrame(self.card, fg_color="transparent")
        header.pack(fill="x", padx=36, pady=(28, 0))

        ctk.CTkLabel(header, text="ЭЖКСР",
                     font=("Inter", 22, "bold"),
                     text_color=TITLE_COLOR).pack(side="left")

        ctk.CTkButton(header, text="Обратно в вход",
                      fg_color="transparent",
                      border_width=1, border_color=INPUT_BORDER,
                      text_color="#475569",
                      hover_color="#F1F5F9",
                      width=160, height=36, corner_radius=8,
                      command=self.on_cancel).pack(side="right")

        # Табы
        tabs = ctk.CTkFrame(self.card, fg_color="transparent")
        tabs.pack(fill="x", padx=36, pady=(16, 8))

        self.btn_student = ctk.CTkButton(
            tabs, text="Студент",
            height=36, corner_radius=8,
            font=("Inter", 13, "bold"),
            command=lambda: self.switch_role("student")
        )
        self.btn_student.pack(side="left", padx=(0, 8))

        self.btn_teacher = ctk.CTkButton(
            tabs, text="Преподаватель",
            height=36, corner_radius=8,
            font=("Inter", 13, "bold"),
            command=lambda: self.switch_role("teacher")
        )
        self.btn_teacher.pack(side="left")

        # Форма
        self.form = ctk.CTkFrame(self.card, fg_color="transparent")
        self.form.pack(fill="both", expand=True, padx=36, pady=16)

        self.current_role = "student"
        self.build_form()
        self._update_tabs()

        # Кнопка завершить
        ctk.CTkButton(
            self.card, text="Завершить",
            font=("Inter", 14, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8",
            height=45, corner_radius=8,
            command=self.on_register
        ).pack(side="right", padx=36, pady=(0, 24))

    def _update_tabs(self):
        #Обновить цвета табов
        if self.current_role == "student":
            self.btn_student.configure(
                fg_color=TAB_ACTIVE_BG, text_color=TAB_ACTIVE_TEXT,
                hover_color=TAB_HOVER, border_width=0)
            self.btn_teacher.configure(
                fg_color=TAB_INACTIVE_BG, text_color=TAB_INACTIVE_TEXT,
                hover_color="#F1F5F9", border_width=1,
                border_color=TAB_INACTIVE_BORDER)
        else:
            self.btn_teacher.configure(
                fg_color=TAB_ACTIVE_BG, text_color=TAB_ACTIVE_TEXT,
                hover_color=TAB_HOVER, border_width=0)
            self.btn_student.configure(
                fg_color=TAB_INACTIVE_BG, text_color=TAB_INACTIVE_TEXT,
                hover_color="#F1F5F9", border_width=1,
                border_color=TAB_INACTIVE_BORDER)

    def build_form(self):
        #Построить форму
        for w in self.form.winfo_children():
            w.destroy()

        left = ctk.CTkFrame(self.form, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right = ctk.CTkFrame(self.form, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))

        self.fio_entry = self._add_field(left, "ФИО", "введите ФИО")
        self.login_entry = self._add_field(left, "Логин", "введите логин")
        self.password_entry = self._add_field(left, "Пароль", "введите пароль", show="•")
        self.confirm_entry = self._add_field(left, "Подтверждение пароля", "повторите пароль", show="•")

        if self.current_role == "student":
            self.group_entry = self._add_field(right, "Ввести группу", "ИСП-34")
            self.email_entry = self._add_field(right, "Электронная почта", "email@mail.com")
            self.direction_entry = None
        else:
            self.email_entry = self._add_field(right, "Электронная почта", "email@mail.com")
            self.direction_entry = self._add_field(right, "Направление", "Информатика")
            self.group_entry = None

    def _add_field(self, parent, label, placeholder, show=None):
        ctk.CTkLabel(parent, text=label,
                     font=("Inter", 12, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", pady=(0, 4))

        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            show=show if show else "",
            text_color="#111010",
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            font=("Inter", 13), height=42, corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 14))
        return entry

    def switch_role(self, role):
        #Переключить роль
        self.current_role = role
        self.build_form()
        self._update_tabs()

    def on_register(self):
        #Зарегистрировать
        from logic.auth import register_student, register_teacher

        fio = self.fio_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not fio or not login or not password:
            messagebox.showwarning("Ошибка", "Заполните обязательные поля")
            return

        if password != confirm:
            messagebox.showwarning("Ошибка", "Пароли не совпадают")
            return

        if len(password) < 6:
            messagebox.showwarning("Ошибка", "Пароль минимум 6 символов")
            return

        if self.current_role == "student":
            success = register_student(
                fio=fio, login=login, password=password,
                group=(self.group_entry.get().strip() if self.group_entry else ""),
                email=(self.email_entry.get().strip() if self.email_entry else "")
            )
        else:
            success = register_teacher(
                fio=fio, login=login, password=password,
                direction=(self.direction_entry.get().strip() if self.direction_entry else ""),
                email=(self.email_entry.get().strip() if self.email_entry else "")
            )

        if success:
            messagebox.showinfo("Успех", "Аккаунт создан!")
            self.on_success()
        else:
            messagebox.showerror("Ошибка", "Логин уже занят")
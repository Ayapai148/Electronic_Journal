"""
Экран авторизации ЭЖКСР.
Соответствует макету: Рисунок 2 — Форма авторизации программы.
"""

import customtkinter as ctk
from tkinter import messagebox


class LoginWindow(ctk.CTk):
    """Окно входа в систему."""

    def __init__(self):
        super().__init__()

        # --- Настройки окна ---
        self.title("ЭЖКСР — Вход")
        self.geometry("1440x1024")
        self.resizable(False, False)

        # Тёмно-синий градиент (имитация через фон)
        self.configure(fg_color="#1E3A8A")

        # --- Центральная карточка ---
        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=520,
            corner_radius=16,
            fg_color="#FFFFFF"
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False)


        # --- Заголовок ---
        ctk.CTkLabel(
            self.card,
            text="ЭЖКСР",
            font=("Inter", 20, "bold"),
            text_color="#1E3A8A"
        ).pack()

        # --- Подзаголовок ---
        ctk.CTkLabel(
            self.card,
            text="Электронный журнал кружковой\nи секционной работы",
            font=("Inter", 12),
            text_color="#64748B",
            justify="center"
        ).pack(pady=(4, 28))

        # --- Поле: Роль ---
        ctk.CTkLabel(
            self.card,
            text="Роль",
            font=("Inter", 13, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", padx=36)

        self.role_var = ctk.StringVar(value="Преподаватель")
        self.role_menu = ctk.CTkOptionMenu(
            self.card,
            values=["Преподаватель", "Студент", "Администратор"],
            variable=self.role_var,
            fg_color="#F8FAFC",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            text_color="#1E293B",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#1E293B",
            dropdown_hover_color="#EFF6FF",
            font=("Inter", 14),
            height=45,
            corner_radius=8
        )
        self.role_menu.pack(fill="x", padx=36, pady=(6, 18))

        # --- Поле: Логин ---
        ctk.CTkLabel(
            self.card,
            text="Логин",
            font=("Inter", 13, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", padx=36)

        self.login_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="введите логин",
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 14),
            height=45,
            corner_radius=8
        )
        self.login_entry.pack(fill="x", padx=36, pady=(6, 18))

        # --- Поле: Пароль ---
        ctk.CTkLabel(
            self.card,
            text="Пароль",
            font=("Inter", 13, "bold"),
            text_color="#334155",
            anchor="w"
        ).pack(fill="x", padx=36)

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="введите пароль",
            show="•",
            fg_color="#F8FAFC",
            border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 14),
            height=45,
            corner_radius=8
        )
        self.password_entry.pack(fill="x", padx=36, pady=(6, 24))

        # --- Кнопка «Войти» ---
        self.login_btn = ctk.CTkButton(
            self.card,
            text="Войти в систему",
            font=("Inter", 14, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=45,
            corner_radius=8,
            command=self.on_login
        )
        self.login_btn.pack(fill="x", padx=36)

        # --- Ссылка «Регистрация» ---
        self.register_link = ctk.CTkLabel(
            self.card,
            text="Нет аккаунта? Зарегистрироваться",
            font=("Inter", 12),
            text_color="#2563EB",
            cursor="hand2"
        )
        self.register_link.pack(pady=(16, 40))
        self.register_link.bind("<Button-1>", lambda e: self.open_register())

    def on_login(self):
        """Обработка нажатия кнопки «Войти»."""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните логин и пароль")
            return

        # Здесь будет вызов logic.auth.authenticate(login, password, role)
        messagebox.showinfo(
            "Успех",
            f"Вход выполнен!\nРоль: {role}\nЛогин: {login}"
        )

    def open_register(self):
        """Открыть окно регистрации."""
        from ui.register import RegisterWindow
        self.destroy()
        app = RegisterWindow()
        app.mainloop()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
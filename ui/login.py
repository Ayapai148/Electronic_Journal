"""
Экран авторизации (Рисунок 2).
"""

import customtkinter as ctk
from tkinter import messagebox


class LoginWindow(ctk.CTk):
    """Окно входа."""

    def __init__(self):
        super().__init__()

        self.title("ЭЖКСР — Вход")
        self.geometry("1440x1024")
        self.resizable(False, False)
        self.configure(fg_color="#1E3A8A")

        card = ctk.CTkFrame(self, width=420, height=520,
                            corner_radius=16, fg_color="#FFFFFF")
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="📓",
                     font=("Segoe UI Emoji", 42)).pack(pady=(40, 8))

        ctk.CTkLabel(card, text="ЭЖКСР",
                     font=("Inter", 20, "bold"),
                     text_color="#1E3A8A").pack()

        ctk.CTkLabel(card,
                     text="Электронный журнал кружковой\nи секционной работы",
                     font=("Inter", 12),
                     text_color="#64748B",
                     justify="center").pack(pady=(4, 28))

        # Роль
        ctk.CTkLabel(card, text="Роль",
                     font=("Inter", 13, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", padx=36)

        self.role_var = ctk.StringVar(value="Преподаватель")
        ctk.CTkOptionMenu(
            card,
            values=["Преподаватель", "Студент", "Администратор"],
            variable=self.role_var,
            fg_color="#F8FAFC",
            button_color="#E2E8F0",
            text_color="#1E293B",
            font=("Inter", 14),
            height=45, corner_radius=8
        ).pack(fill="x", padx=36, pady=(6, 18))

        # Логин
        ctk.CTkLabel(card, text="Логин",
                     font=("Inter", 13, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", padx=36)

        self.login_entry = ctk.CTkEntry(
            card, placeholder_text="введите логин",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.login_entry.pack(fill="x", padx=36, pady=(6, 18))

        # Пароль
        ctk.CTkLabel(card, text="Пароль",
                     font=("Inter", 13, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", padx=36)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="введите пароль",
            show="•",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.password_entry.pack(fill="x", padx=36, pady=(6, 24))

        # Войти
        ctk.CTkButton(
            card, text="Войти в систему",
            font=("Inter", 14, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8",
            height=45, corner_radius=8,
            command=self.on_login
        ).pack(fill="x", padx=36)

        # Ссылка регистрации
        link = ctk.CTkLabel(
            card,
            text="Нет аккаунта? Зарегистрироваться",
            font=("Inter", 12),
            text_color="#2563EB",
            cursor="hand2"
        )
        link.pack(pady=(16, 40))
        link.bind("<Button-1>", lambda e: self.open_register())

    def on_login(self):
        """Вход."""
        from logic.auth import authenticate

        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        user = authenticate(login, password)
        if user is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        self.destroy()
        role = user["role"]

        if role == "teacher":
            from ui.teacher.dashboard import TeacherDashboard
            app = TeacherDashboard(user)
        elif role == "admin":
            from ui.admin.dashboard import AdminDashboard
            app = AdminDashboard(user)
        else:
            from ui.student.dashboard import StudentDashboard
            app = StudentDashboard(user)

        app.mainloop()

    def open_register(self):
        """Открыть регистрацию (Рисунки 3-4)."""
        from ui.register import RegisterWindow
        self.destroy()
        app = RegisterWindow()
        app.mainloop()
import customtkinter as ctk
from tkinter import messagebox


BG_COLOR = "#1E3A8A"
CARD_BG = "#FFFFFF"
TITLE_COLOR = "#1E3A8A"
TEXT_GRAY = "#64748B"
LABEL_COLOR = "#334155"
INPUT_BG = "#F8FAFC"
INPUT_BORDER = "#CBD5E1"
BTN_BG = "#2563EB"
BTN_HOVER = "#1D4ED8"
BTN_TEXT = "#FFFFFF"
LINK_COLOR = "#2563EB"


class LoginPage(ctk.CTkFrame):

    def __init__(self, parent, on_success, on_register):
        super().__init__(parent, fg_color=BG_COLOR)

        self.on_success = on_success
        self.on_register = on_register

        card = ctk.CTkFrame(self, width=420, height=520,
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
                     justify="center").pack(pady=(4, 20))

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
        ).pack(fill="x", padx=36, pady=(6, 14))

        ctk.CTkLabel(card, text="Логин",
                     font=("Inter", 13, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", padx=36)

        self.login_entry = ctk.CTkEntry(
            card, placeholder_text="введите логин",
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.login_entry.pack(fill="x", padx=36, pady=(6, 14))

        ctk.CTkLabel(card, text="Пароль",
                     font=("Inter", 13, "bold"),
                     text_color=LABEL_COLOR,
                     anchor="w").pack(fill="x", padx=36)

        self.password_entry = ctk.CTkEntry(
            card, placeholder_text="введите пароль",
            show="•",
            fg_color=INPUT_BG, border_color=INPUT_BORDER,
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 14), height=45, corner_radius=8
        )
        self.password_entry.pack(fill="x", padx=36, pady=(6, 20))

        self.login_btn = ctk.CTkButton(
            card, text="Войти в систему",
            font=("Inter", 14, "bold"),
            fg_color=BTN_BG, hover_color=BTN_HOVER,
            text_color=BTN_TEXT,
            height=45, corner_radius=8,
            command=self.on_login
        )
        self.login_btn.pack(fill="x", padx=36)

        links = ctk.CTkFrame(card, fg_color="transparent")
        links.pack(pady=(14, 30))

        forgot = ctk.CTkLabel(
            links,
            text="Забыли пароль?",
            font=("Inter", 12),
            text_color=LINK_COLOR,
            cursor="hand2"
        )
        forgot.pack(side="left", padx=(0, 12))
        forgot.bind("<Button-1>", lambda e: self.open_forgot())

        reg = ctk.CTkLabel(
            links,
            text="Регистрация",
            font=("Inter", 12),
            text_color=LINK_COLOR,
            cursor="hand2"
        )
        reg.pack(side="left")
        reg.bind("<Button-1>", lambda e: self.on_register())

    def on_login(self):
        from logic.auth import authenticate

        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        selected_role = self.role_var.get()

        if not login or not password:
            messagebox.showwarning("Ошибка", "Заполните логин и пароль")
            return

        user = authenticate(login, password)

        if user is None:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        role_map = {
            "Преподаватель": "teacher",
            "Студент": "student",
            "Администратор": "admin",
        }

        expected_role = role_map.get(selected_role)
        actual_role = user.get("role")

        if expected_role != actual_role:
            role_ru = {
                "admin": "администратор",
                "teacher": "преподаватель",
                "student": "студент",
            }.get(actual_role, actual_role)
            messagebox.showerror(
                "Ошибка",
                f"Вы выбрали роль «{selected_role}»,\n"
                f"но этот пользователь — {role_ru}."
            )
            return

        self.on_success(user)

    def open_forgot(self):
        dialog = ForgotPasswordDialog(self)
        dialog.grab_set()


class ForgotPasswordDialog(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Восстановление пароля")
        self.geometry("440x560")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        self.reset_id = None
        self.email = None

        self.card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        self.card.pack(fill="both", expand=True, padx=32, pady=24)

        self._show_step_email()

    def _show_step_email(self):
        for w in self.card.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.card, text="Восстановление пароля",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.card,
                     text="Введите email, указанный при регистрации",
                     font=("Inter", 12),
                     text_color="#64748B",
                     anchor="w").pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(self.card, text="Email",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.email_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="email@example.com",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.email_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            self.card, text="Отправить код",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_send_code
        ).pack(fill="x")

        ctk.CTkButton(
            self.card, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(fill="x", pady=(8, 0))

    def _on_send_code(self):
        from logic.auth import (
            find_user_by_email, generate_reset_code,
            save_reset_code, send_email,
        )

        email = self.email_entry.get().strip()

        if not email:
            messagebox.showwarning("Ошибка", "Введите email")
            return

        user = find_user_by_email(email)

        if not user:
            messagebox.showerror("Ошибка",
                                 "Пользователь с таким email не найден")
            return

        code = generate_reset_code()
        save_reset_code(user["id"], email, code)
        send_email(
            to=email,
            subject="Восстановление пароля ЭЖКСР",
            body=f"Ваш код подтверждения: {code}"
        )

        self.email = email

        messagebox.showinfo(
            "Код отправлен",
            f"Код отправлен на {email}\n\n"
            f"(В учебной версии код выведен в консоль)"
        )

        self._show_step_code()

    def _show_step_code(self):
        for w in self.card.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.card, text="Введите код",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.card,
                     text=f"Код отправлен на {self.email}",
                     font=("Inter", 12),
                     text_color="#64748B",
                     anchor="w").pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(self.card, text="Код из письма",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.code_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="6-значный код",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.code_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(self.card, text="Новый пароль",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="минимум 6 символов",
            show="•",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.password_entry.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(self.card, text="Подтверждение пароля",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.confirm_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="повторите пароль",
            show="•",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.confirm_entry.pack(fill="x", pady=(0, 20))

        ctk.CTkButton(
            self.card, text="Сменить пароль",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_change_password
        ).pack(fill="x")

        ctk.CTkButton(
            self.card, text="Назад",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self._show_step_email
        ).pack(fill="x", pady=(8, 0))

    def _on_change_password(self):
        from logic.auth import (
            verify_reset_code, update_password,
            mark_code_used,
        )

        code = self.code_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if not code or not password or not confirm:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        if password != confirm:
            messagebox.showwarning("Ошибка", "Пароли не совпадают")
            return

        if len(password) < 6:
            messagebox.showwarning("Ошибка", "Пароль минимум 6 символов")
            return

        reset = verify_reset_code(self.email, code)

        if not reset:
            messagebox.showerror("Ошибка", "Неверный код")
            return

        if update_password(reset["user_id"], password):
            mark_code_used(reset["id"])
            messagebox.showinfo("Успех", "Пароль изменён")
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось изменить пароль")
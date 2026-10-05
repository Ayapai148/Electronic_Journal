"""
Панель администратора (Рисунки 16, 17, 19 из отчёта).

Единый фрейм с 3 страницами:
- Панель управления
- Пользователи
- Отчёты
"""

import customtkinter as ctk
from tkinter import messagebox
from ui.theme import (
    HEADER_BG, SIDEBAR_BG, CONTENT_BG, CARD_BG,
    TEXT_DARK, TEXT_GRAY, TEXT_BLUE, MENU_ACTIVE,
    MENU_TEXT, BORDER
)


# Ширины колонок
COL_ID = 80
COL_FIO = 340
COL_LOGIN = 180
COL_ROLE = 200
COL_DATE = 160
COL_ACTION = 180

COL_CLUB = 260
COL_TEACHER = 240
COL_STUDENTS = 140
COL_AVG = 140
COL_ATT = 160


class AdminApp(ctk.CTkFrame):
    """Фрейм администратора со всеми страницами."""

    def __init__(self, parent, user, on_logout):
        super().__init__(parent, fg_color=CONTENT_BG)

        self.user = user
        self.on_logout = on_logout

        self.current_page = "dashboard"

        # Шапка
        self._build_header()

        # Layout
        layout = ctk.CTkFrame(self, fg_color="transparent")
        layout.pack(fill="both", expand=True)

        self._build_sidebar(layout)

        self.content = ctk.CTkFrame(layout, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True,
                          padx=32, pady=28)

        self.show_page("dashboard")

    # ============================================================
    # ШАПКА
    # ============================================================

    def _build_header(self):
        header = ctk.CTkFrame(self, height=60,
                              fg_color=HEADER_BG, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header,
                     text="ЭЖКСР - Электронный журнал",
                     font=("Inter", 16, "bold"),
                     text_color="#FFFFFF").pack(side="left", padx=24)

        ctk.CTkButton(header, text="Выйти",
                      fg_color="transparent",
                      border_width=1, border_color="#FFFFFF",
                      hover_color="#1D4ED8",
                      width=100, height=32,
                      command=self.on_logout).pack(side="right", padx=24)

        ctk.CTkLabel(header,
                     text=f"{self.user.get('login', 'Администратор')}  •  Администратор",
                     font=("Inter", 13),
                     text_color="#FFFFFF").pack(side="right", padx=16)

    # ============================================================
    # САЙДБАР
    # ============================================================

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=240,
                               fg_color=SIDEBAR_BG, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self.menu_buttons = {}

        menu_items = [
            ("Панель управления", "dashboard"),
            ("Пользователи", "users"),
            ("Кружки", "clubs"),
            ("Отчёты", "reports"),
        ]

        for text, page in menu_items:
            btn = ctk.CTkButton(
                sidebar, text=text, anchor="w",
                fg_color="transparent", text_color=MENU_TEXT,
                hover_color=MENU_ACTIVE,
                height=44, corner_radius=0,
                font=("Inter", 14),
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(fill="x")
            self.menu_buttons[page] = btn

    def _update_menu(self):
        for page, btn in self.menu_buttons.items():
            is_active = (page == self.current_page)
            btn.configure(
                fg_color=MENU_ACTIVE if is_active else "transparent",
                text_color="#2563EB" if is_active else MENU_TEXT,
                font=("Inter", 14, "bold" if is_active else "normal")
            )

    # ============================================================
    # ПЕРЕКЛЮЧЕНИЕ
    # ============================================================

    def show_page(self, page):
        self.current_page = page
        self._update_menu()

        for w in self.content.winfo_children():
            w.destroy()

        if page == "dashboard":
            self._show_dashboard()
        elif page == "users":
            self._show_users()
        elif page =="clubs":
            self._show_clubs()
        elif page == "reports":
            self._show_reports()

    # ============================================================
    # ПАНЕЛЬ УПРАВЛЕНИЯ
    # ============================================================

    def _show_dashboard(self):
        from logic.admin import (
            get_users_count, get_students_count,
            get_teachers_count, get_clubs_count,
            get_recent_actions,
        )

        ctk.CTkLabel(self.content, text="Панель администратора",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Управление пользователями, ролями и отчётность",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        # Карточки
        users = get_users_count()
        students = get_students_count()
        teachers = get_teachers_count()
        clubs = get_clubs_count()

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x")

        for label, value in [
            ("ПОЛЬЗОВАТЕЛЕЙ", str(users)),
            ("КРУЖКОВ И СЕКЦИЙ", str(clubs)),
            ("СТУДЕНТОВ", str(students)),
            ("ПРЕПОДАВАТЕЛЕЙ", str(teachers)),
        ]:
            card = ctk.CTkFrame(cards, fg_color=CARD_BG,
                                corner_radius=12, border_width=1,
                                border_color=BORDER)
            card.pack(side="left", expand=True, fill="both", padx=6)

            ctk.CTkLabel(card, text=label,
                         font=("Inter", 11, "bold"),
                         text_color=TEXT_GRAY,
                         anchor="w").pack(anchor="w", padx=20, pady=(20, 4))

            ctk.CTkLabel(card, text=value,
                         font=("Inter", 28, "bold"),
                         text_color=TEXT_BLUE,
                         anchor="w").pack(anchor="w", padx=20, pady=(0, 20))

        # Последние действия
        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True, pady=(24, 0))

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Последние действия",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        actions = get_recent_actions()

        if not actions:
            ctk.CTkLabel(panel, text="Нет данных",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [("Дата", 200), ("Пользователь", 240), ("Действие", 500)]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, a in enumerate(actions):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (a.get("date", "—"), 200),
                (a.get("user", "—"), 240),
                (a.get("action", "—"), 500),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(actions) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # ПОЛЬЗОВАТЕЛИ
    # ============================================================

    def _show_users(self):
        from logic.admin import get_all_users

        ctk.CTkLabel(self.content, text="Пользователи",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Список всех пользователей системы",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        users = get_all_users()

        # Панель
        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        # Заголовок панели
        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Список пользователей",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkButton(h, text="+ Добавить пользователя",
                      fg_color="#2563EB", hover_color="#1D4ED8",
                      height=32, corner_radius=8,
                      font=("Inter", 12, "bold"),
                      command=self._on_add_user).pack(side="right")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not users:
            ctk.CTkLabel(panel, text="Нет пользователей",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # === ЗАГОЛОВКИ ТАБЛИЦЫ (фиксированные, не скроллятся) ===
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [
            ("ID", COL_ID), ("ФИО", COL_FIO), ("Логин", COL_LOGIN),
            ("Роль", COL_ROLE), ("Дата создания", COL_DATE),
            ("Действия", COL_ACTION),
        ]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        # === ПРОКРУЧИВАЕМАЯ ОБЛАСТЬ С ДАННЫМИ ===
        scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
            corner_radius=0
        )
        scroll.pack(fill="both", expand=True)

        # Данные
        for r_idx, u in enumerate(users):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x")

            for value, w in [
                (str(u.get("id", "-")), COL_ID),
                (u.get("fio", "-"), COL_FIO),
                (u.get("login", "-"), COL_LOGIN),
                (self._role_text(u.get("role")), COL_ROLE),
                (u.get("create_date") or "-", COL_DATE),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            # Кнопки действий
            actions = ctk.CTkFrame(row, width=COL_ACTION, fg_color="transparent")
            actions.pack(side="left", padx=14, pady=11)

            ctk.CTkButton(actions, text="удалить",
                          fg_color="#FEE2E2", hover_color="#FECACA",
                          text_color="#991B1B",
                          width=80, height=28,
                          command=lambda uid=u.get("id"),
                                         ulogin=u.get("login"):
                              self._on_delete_user(uid, ulogin)
                          ).pack(side="left")

            if r_idx < len(users) - 1:
                ctk.CTkFrame(scroll, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    def _role_text(self, role):
        return {
            "admin": "Администратор",
            "teacher": "Преподаватель",
            "student": "Студент",
        }.get(role, role or "—")

    def _on_delete_user(self, user_id, login):
        """Удалить пользователя с подтверждением."""
        from logic.admin import delete_user

        # Нельзя удалить самого себя
        if self.user.get("id") == user_id:
            messagebox.showwarning("Ошибка", "Нельзя удалить себя")
            return

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить пользователя «{login}»?"
        )

        if not confirm:
            return

        if delete_user(user_id, login, admin=self.user):
            messagebox.showinfo("Успех", "Пользователь удалён")
            self.show_page("users")
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    # ============================================================
    # ОТЧЁТЫ
    # ============================================================

    def _show_reports(self):
        from logic.admin import get_clubs_report

        ctk.CTkLabel(self.content, text="Отчёты",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Сводка по кружкам и секциям",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        report = get_clubs_report()

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Сводка по кружкам и секциям",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not report:
            ctk.CTkLabel(panel, text="Нет данных",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [
            ("Кружок/секция", COL_CLUB),
            ("Преподаватель", COL_TEACHER),
            ("Студентов", COL_STUDENTS),
            ("Средний балл", COL_AVG),
            ("Посещаемость", COL_ATT),
        ]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        # Данные
        for r_idx, row_data in enumerate(report):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")

            avg = row_data.get("avg_grade") or 0
            att = row_data.get("attendance") or 0

            for value, w in [
                (row_data.get("club", "-"), COL_CLUB),
                (row_data.get("teacher", "-"), COL_TEACHER),
                (str(row_data.get("students", 0)), COL_STUDENTS),
                (f"{avg:.1f}" if avg else "-", COL_AVG),
                (f"{att}%" if att else "-", COL_ATT),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(report) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")
    def _on_add_user(self):
            """Открыть модальное окно добавления пользователя."""
            dialog = AddUserDialog(
                self,
                on_success=self._reload_users,
                admin=self.user
            )
            dialog.grab_set()   # модальное окно
    
    def _reload_users(self):
        """Перезагрузить страницу пользователей."""
        self.show_page("users")
    def _show_clubs(self):
        """Страница «Кружки»."""
        from logic.admin import get_all_clubs

        ctk.CTkLabel(self.content, text="Кружки и секции",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Список всех кружков и секций колледжа",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        clubs = get_all_clubs()

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Список кружков",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkButton(h, text="+ Добавить кружок",
                      fg_color="#2563EB", hover_color="#1D4ED8",
                      height=32, corner_radius=8,
                      font=("Inter", 12, "bold"),
                      command=self._on_add_club).pack(side="right")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not clubs:
            ctk.CTkLabel(panel, text="Нет кружков",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        columns = [
            ("Название", 240),
            ("Тип", 140),
            ("Преподаватель", 220),
            ("Расписание", 260),
            ("Аудитория", 120),
            ("Действия", 200),
        ]

        # Заголовки — через grid (как данные)
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")

        for col_idx, (title, width) in enumerate(columns):
            head.grid_columnconfigure(col_idx, weight=0, minsize=width)
            ctk.CTkLabel(head, text=title,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").grid(
                row=0, column=col_idx,
                sticky="w", padx=14, pady=11
            )

                # Прокручиваемая область
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent",
                                        scrollbar_button_color="#CBD5E1")
        scroll.pack(fill="both", expand=True)

        # Список колонок с фиксированной шириной
        columns = [
            ("Название", 240),
            ("Тип", 140),
            ("Преподаватель", 220),
            ("Расписание", 260),
            ("Аудитория", 120),
            ("Действия", 200),
        ]

        for r_idx, c in enumerate(clubs):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x")

            # Используем grid с фиксированными колонками
            for col_idx, (_, width) in enumerate(columns):
                row.grid_columnconfigure(col_idx, weight=0, minsize=width)

            # Данные
            values = [
                c.get("name", "-"),
                c.get("type") or "-",
                c.get("teacher_fio", "-"),
                c.get("schedule") or "-",
                c.get("room") or "-",
            ]

            for col_idx, value in enumerate(values):
                ctk.CTkLabel(row, text=value,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").grid(
                    row=0, column=col_idx,
                    sticky="w", padx=14, pady=11
                )

            # Действия — отдельный фрейм в 6-й колонке
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=5, sticky="w", padx=14, pady=11)

            ctk.CTkButton(actions, text="изменить",
                          fg_color="transparent", border_width=1,
                          border_color=BORDER, text_color=MENU_TEXT,
                          hover_color=MENU_ACTIVE,
                          width=80, height=28,
                          command=lambda club=c: self._on_edit_club(club)
                          ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(actions, text="удалить",
                          fg_color="#FEE2E2", hover_color="#FECACA",
                          text_color="#991B1B",
                          width=80, height=28,
                          command=lambda cid=c.get("id"),
                                         cname=c.get("name"):
                              self._on_delete_club(cid, cname)
                          ).pack(side="left")

            if r_idx < len(clubs) - 1:
                ctk.CTkFrame(scroll, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    def _on_add_club(self):
        """Открыть модалку добавления кружка."""
        dialog = AddClubDialog(
            self, 
            on_success=self._reload_clubs, 
            club=None,
            admin=self.user
        )
        dialog.grab_set()

    def _on_edit_club(self, club):
        """Открыть модалку редактирования кружка."""
        dialog = AddClubDialog(
            self, 
            on_success=self._reload_clubs, 
            club=club,
            admin=self.user
        )
        dialog.grab_set()

    def _on_delete_club(self, club_id, club_name):
        """Удалить кружок с подтверждением."""
        from logic.admin import delete_club

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить кружок «{club_name}»?\n"
            f"Все занятия и записи будут удалены."
        )

        if not confirm:
            return

        if delete_club(club_id, club_name, admin=self.user):
            messagebox.showinfo("Успех", "Кружок удалён")
            self._reload_clubs()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    def _reload_clubs(self):
        """Перезагрузить страницу кружков."""
        self.show_page("clubs")
        
# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ
# ============================================================

class AddUserDialog(ctk.CTkToplevel):
    """Модальное окно добавления пользователя."""

    def __init__(self, parent, on_success, admin):
        super().__init__(parent)
        self.admin = admin

        self.on_success = on_success

        # --- Настройки окна ---
        self.title("Добавить пользователя")
        self.geometry("500x600")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")

        # Центрируем относительно parent
        self.transient(parent)

        # Карточка
        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=36, pady=28)

        # Заголовок
        ctk.CTkLabel(card, text="Добавить пользователя",
                     font=("Inter", 20, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 24))

        # --- Роль ---
        ctk.CTkLabel(card, text="Роль",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.role_var = ctk.StringVar(value="Студент")
        ctk.CTkOptionMenu(
            card,
            values=["Студент", "Преподаватель", "Администратор"],
            variable=self.role_var,
            fg_color="#F8FAFC",
            button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # --- ФИО ---
        self.fio_entry = self._add_field(card, "ФИО", "Иванов Иван Иванович")

        # --- Логин ---
        self.login_entry = self._add_field(card, "Логин", "ivanov")

        # --- Пароль ---
        self.password_entry = self._add_field(
            card, "Пароль", "минимум 6 символов", show="•"
        )

        # --- Дополнительное поле (группа / направление) ---
        self.extra_label = ctk.CTkLabel(
            card, text="Группа",
            font=("Inter", 12, "bold"),
            text_color="#334155",
            anchor="w"
        )
        self.extra_label.pack(fill="x", pady=(0, 4))

        self.extra_entry = ctk.CTkEntry(
            card, placeholder_text="ИСП-34",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.extra_entry.pack(fill="x", pady=(0, 20))

        # Обновляем подпись при смене роли
        self.role_var.trace_add(
            "write",
            lambda *a: self._on_role_change()
        )

        # --- Кнопки ---
        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569",
            hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Создать",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_create
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _add_field(self, parent, label, placeholder, show=None):
        """Создать поле с подписью."""
        ctk.CTkLabel(parent, text=label,
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            show=show if show else "",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 14))
        return entry

    def _on_role_change(self):
        """Обновить подпись доп. поля при смене роли."""
        role = self.role_var.get()
        if role == "Студент":
            self.extra_label.configure(text="Группа")
            self.extra_entry.configure(placeholder_text="ИСП-34")
        elif role == "Преподаватель":
            self.extra_label.configure(text="Направление")
            self.extra_entry.configure(placeholder_text="Информатика")
        else:
            self.extra_label.configure(text="—")
            self.extra_entry.configure(placeholder_text="")

    def _on_create(self):
        """Создать пользователя."""
        from logic.admin import create_user_with_profile

        role = self.role_var.get()
        fio = self.fio_entry.get().strip()
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        extra = self.extra_entry.get().strip()

        # Валидация
        if not fio or not login or not password:
            messagebox.showwarning("Ошибка", "Заполните обязательные поля")
            return

        if len(password) < 6:
            messagebox.showwarning("Ошибка", "Пароль минимум 6 символов")
            return

        role_key = {
            "Студент": "student",
            "Преподаватель": "teacher",
            "Администратор": "admin",
        }.get(role, "student")

        # Создаём
        success = create_user_with_profile(
            fio=fio,
            login=login,
            password=password,
            role=role_key,
            group=extra if role_key == "student" else "",
            direction=extra if role_key == "teacher" else "",
            admin=self.admin   # ← передаём текущего админа
        )

        if success:
            messagebox.showinfo("Успех", "Пользователь создан")
            self.on_success()   # перезагрузить список
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Логин уже занят")

# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВИТЬ / РЕДАКТИРОВАТЬ КРУЖОК
# ============================================================

class AddClubDialog(ctk.CTkToplevel):
    """Модальное окно добавления/редактирования кружка."""

    def __init__(self, parent, on_success, club=None, admin=None):
        """
        Args:
            parent: родитель
            on_success: функция после успеха
            club: если None — добавление, если dict — редактирование
        """
        super().__init__(parent)
        self.admin = admin

        self.on_success = on_success
        self.club = club
        self.is_edit = club is not None

        self.title("Редактировать кружок" if self.is_edit else "Добавить кружок")
        self.geometry("500x620")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        # Карточка
        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=36, pady=28)

        # Заголовок
        title = "Редактировать кружок" if self.is_edit else "Добавить кружок"
        ctk.CTkLabel(card, text=title,
                     font=("Inter", 20, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 24))

        # Название
        self.name_entry = self._add_field(card, "Название", "Робототехника")

        # Тип
        ctk.CTkLabel(card, text="Тип",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.type_var = ctk.StringVar(value="Кружок")
        ctk.CTkOptionMenu(
            card, values=["Кружок", "Секция"],
            variable=self.type_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # Преподаватель
        ctk.CTkLabel(card, text="Преподаватель",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        from logic.admin import get_all_teachers_for_select
        teachers = get_all_teachers_for_select()

        if teachers:
            teacher_names = [f"{t['id']} — {t['fio']}" for t in teachers]
            self.teacher_var = ctk.StringVar(value=teacher_names[0])
        else:
            teacher_names = ["Нет преподавателей"]
            self.teacher_var = ctk.StringVar(value="Нет преподавателей")

        ctk.CTkOptionMenu(
            card, values=teacher_names,
            variable=self.teacher_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # Расписание
        self.schedule_entry = self._add_field(
            card, "Расписание",
            "Пн 15:00-16:30, Ср 15:00-16:30"
        )

        # Аудитория
        self.room_entry = self._add_field(card, "Аудитория", "204")

        # Заполняем поля при редактировании
        if self.is_edit:
            self.name_entry.insert(0, club.get("name") or "")
            self.type_var.set(club.get("type") or "Кружок")
            self.schedule_entry.insert(0, club.get("schedule") or "")
            self.room_entry.insert(0, club.get("room") or "")

            # Выбираем текущего преподавателя
            teacher_id = club.get("teacher_id")
            if teacher_id:
                for name in teacher_names:
                    if name.startswith(f"{teacher_id} "):
                        self.teacher_var.set(name)
                        break

        # Кнопки
        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569",
            hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Сохранить" if self.is_edit else "Создать",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_save
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _add_field(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label,
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            placeholder_text_color="#94A3B8",
            font=("Inter", 13), height=40, corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 14))
        return entry

    def _on_save(self):
        """Сохранить кружок."""
        from logic.admin import create_club, update_club

        name = self.name_entry.get().strip()
        type_ = self.type_var.get()
        schedule = self.schedule_entry.get().strip()
        room = self.room_entry.get().strip()

        # Парсим teacher_id из строки "3 — Иванов Иван"
        teacher_str = self.teacher_var.get()
        try:
            teacher_id = int(teacher_str.split(" — ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Ошибка", "Выберите преподавателя")
            return

        # Валидация
        if not name:
            messagebox.showwarning("Ошибка", "Введите название")
            return

        if not schedule:
            messagebox.showwarning("Ошибка", "Введите расписание")
            return

        # Создание или обновление
        if self.is_edit:
            success = update_club(
                self.club["id"], 
                name, 
                type_,
                teacher_id, 
                schedule, 
                room,
                admin=self.admin
        )
        else:
            success = create_club(
                name, 
                type_, 
                teacher_id, 
                schedule, 
                room,
                admin=self.admin
        )

        if success:
            messagebox.showinfo("Успех",
                                "Кружок обновлён" if self.is_edit
                                else "Кружок создан")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")
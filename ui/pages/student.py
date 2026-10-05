"""
Панель студента со всеми страницами.
"""

import customtkinter as ctk
from ui.theme import (
    HEADER_BG, SIDEBAR_BG, CONTENT_BG, CARD_BG,
    TEXT_DARK, TEXT_GRAY, TEXT_BLUE, MENU_ACTIVE,
    MENU_TEXT, BORDER
)


class StudentApp(ctk.CTkFrame):
    """Фрейм студента со всеми страницами."""

    def __init__(self, parent, user, on_logout):
        super().__init__(parent, fg_color=CONTENT_BG)

        self.user = user
        self.on_logout = on_logout

        # Профиль
        from logic.student import get_student_by_user_id
        self.student = get_student_by_user_id(user["id"])

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
                     text="📓  ЭЖКСР — Электронный журнал",
                     font=("Inter", 16, "bold"),
                     text_color="#FFFFFF").pack(side="left", padx=24)

        ctk.CTkButton(header, text="Выйти",
                      fg_color="transparent",
                      border_width=1, border_color="#FFFFFF",
                      hover_color="#1D4ED8",
                      width=100, height=32,
                      command=self.on_logout).pack(side="right", padx=24)

        ctk.CTkLabel(header,
                     text=f"{self.user.get('login', 'Студент')}  •  Студент",
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
            ("Главная", "dashboard"),
            ("Расписание", "schedule"),
            ("Мои оценки", "grades"),
            ("Преподаватели и группа", "people"),
            ("Портфолио", "portfolio"),
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
        elif page == "schedule":
            self._show_schedule()
        elif page == "grades":
            self._show_grades()
        elif page == "people":
            self._show_people()
        elif page == "portfolio":
            self._show_portfolio()

    # ============================================================
    # ГЛАВНАЯ
    # ============================================================

    def _show_dashboard(self):
        from logic.student import (
            get_clubs_count, get_average_grade,
            get_attendance_rate, get_achievements_count,
            get_upcoming_lessons,
        )

        ctk.CTkLabel(self.content, text="Главная",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        if not self.student:
            ctk.CTkLabel(self.content, text="Нет данных о студенте",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        fio = f"{self.student['surname']} {self.student['name']}"
        if self.student.get("patronymic"):
            fio += f" {self.student['patronymic']}"
        group = self.student.get("groups") or "—"

        ctk.CTkLabel(self.content,
                     text=f"{fio} — группа {group}",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        sid = self.student["id"]
        clubs = get_clubs_count(sid)
        avg = get_average_grade(sid)
        rate = get_attendance_rate(sid)
        ach = get_achievements_count(sid)

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x")

        for label, value in [
            ("МОИ КРУЖКИ", str(clubs)),
            ("СРЕДНИЙ БАЛЛ", f"{avg}" if avg is not None else "—"),
            ("ПОСЕЩАЕМОСТЬ", f"{rate}%" if rate is not None else "—"),
            ("ДОСТИЖЕНИЙ", str(ach)),
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

        # Занятия
        lessons = get_upcoming_lessons(sid)

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True, pady=(24, 0))

        ph = ctk.CTkFrame(panel, fg_color="transparent")
        ph.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(ph, text="Ближайшие занятия",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not lessons:
            ctk.CTkLabel(panel, text="Нет занятий",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        head_row = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head_row.pack(fill="x")
        for text, w in [("Дата", 140), ("Тема", 300),
                        ("Кружок", 200), ("Преподаватель", 200),
                        ("Аудитория", 120)]:
            ctk.CTkLabel(head_row, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, lesson in enumerate(lessons):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")

            for value, w in [
                (lesson.get("date", "—"), 140),
                (lesson.get("topic", "—"), 300),
                (lesson.get("club_name", "—"), 200),
                (lesson.get("teacher_fio", "—"), 200),
                (lesson.get("room", "—"), 120),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(lessons) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # РАСПИСАНИЕ
    # ============================================================

    def _show_schedule(self):
        from logic.student import get_schedule

        ctk.CTkLabel(self.content, text="Расписание",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content, text="Расписание занятий на неделю",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.student:
            ctk.CTkLabel(self.content, text="Нет данных о студенте",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        schedule = get_schedule(self.student["id"])
        total = sum(len(ls) for ls in schedule.values())

        if total == 0:
            ctk.CTkLabel(self.content, text="Расписание не составлено",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        days_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        days_frame.pack(fill="both", expand=True)

        for day_name, lessons in schedule.items():
            day_card = ctk.CTkFrame(days_frame, fg_color="#F8FAFC",
                                    corner_radius=10, border_width=1,
                                    border_color=BORDER)
            day_card.pack(side="left", expand=True, fill="both", padx=6)

            ctk.CTkLabel(day_card, text=day_name,
                         font=("Inter", 12, "bold"),
                         text_color="#1E3A8A",
                         anchor="w").pack(fill="x", padx=16, pady=(16, 10))

            if not lessons:
                ctk.CTkLabel(day_card, text="Нет занятий",
                             font=("Inter", 12),
                             text_color="#94A3B8",
                             anchor="w").pack(fill="x", padx=16, pady=6)
                continue

            for lesson in lessons:
                item = ctk.CTkFrame(day_card, fg_color="#FFFFFF",
                                    corner_radius=6)
                item.pack(fill="x", padx=12, pady=4)

                ctk.CTkLabel(item, text=lesson["time"],
                             font=("Inter", 11, "bold"),
                             text_color="#2563EB",
                             anchor="w").pack(fill="x", padx=10, pady=(8, 0))

                ctk.CTkLabel(item, text=lesson["club"],
                             font=("Inter", 12),
                             text_color=TEXT_DARK,
                             anchor="w").pack(fill="x", padx=10)

                ctk.CTkLabel(item, text=f"Ауд. {lesson['room']}",
                             font=("Inter", 10),
                             text_color="#94A3B8",
                             anchor="w").pack(fill="x", padx=10)

                ctk.CTkLabel(item, text=lesson["teacher"],
                             font=("Inter", 10),
                             text_color="#94A3B8",
                             anchor="w").pack(fill="x", padx=10, pady=(0, 8))

    # ============================================================
    # ОЦЕНКИ
    # ============================================================

    def _show_grades(self):
        from logic.student import get_grades

        ctk.CTkLabel(self.content, text="Мои оценки",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content, text="Успеваемость по кружкам и секциям",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.student:
            ctk.CTkLabel(self.content, text="Нет данных о студенте",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        grades = get_grades(self.student["id"])

        if not grades:
            ctk.CTkLabel(self.content, text="Пока нет оценок",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        grouped = {}
        for g in grades:
            club = g.get("club_name", "Без кружка")
            grouped.setdefault(club, []).append(g)

        for club_name, club_grades in grouped.items():
            teacher = club_grades[0].get("teacher_fio", "—") if club_grades else "—"

            panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                                 corner_radius=12, border_width=1,
                                 border_color=BORDER)
            panel.pack(fill="x", pady=(0, 16))

            h = ctk.CTkFrame(panel, fg_color="transparent")
            h.pack(fill="x", padx=22, pady=16)
            ctk.CTkLabel(h, text=f"{club_name} — {teacher}",
                         font=("Inter", 15, "bold"),
                         text_color=TEXT_DARK).pack(side="left")

            ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

            head_row = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
            head_row.pack(fill="x")
            for text, w in [("Дата", 140), ("Тема занятия", 400),
                            ("Оценка", 100), ("Примечание", 300)]:
                ctk.CTkLabel(head_row, text=text, width=w,
                             font=("Inter", 12, "bold"),
                             text_color=MENU_TEXT,
                             anchor="w").pack(side="left", padx=14, pady=11)

            for r_idx, g in enumerate(club_grades):
                row = ctk.CTkFrame(panel, fg_color="transparent")
                row.pack(fill="x")

                for value, w in [
                    (g.get("date", "—"), 140),
                    (g.get("topic", "—"), 400),
                    (str(g.get("grade")) if g.get("grade") is not None else "—", 100),
                    (g.get("comment") or "—", 300),
                ]:
                    ctk.CTkLabel(row, text=value, width=w,
                                 font=("Inter", 13),
                                 text_color="#334155",
                                 anchor="w").pack(side="left", padx=14, pady=11)

                if r_idx < len(club_grades) - 1:
                    ctk.CTkFrame(panel, height=1,
                                 fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # ПРЕПОДАВАТЕЛИ И ГРУППА
    # ============================================================

    def _show_people(self):
        from logic.student import get_teachers_list, get_groupmates

        ctk.CTkLabel(self.content, text="Преподаватели и группа",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content, text="Список преподавателей и одногруппников",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.student:
            return

        # Преподаватели
        teachers = get_teachers_list()

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="x", pady=(0, 16))

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Преподаватели",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not teachers:
            ctk.CTkLabel(panel, text="Нет данных о преподавателях",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
        else:
            head_row = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
            head_row.pack(fill="x")
            for text, w in [("ФИО", 340), ("Должность", 240), ("Кружки", 300)]:
                ctk.CTkLabel(head_row, text=text, width=w,
                             font=("Inter", 12, "bold"),
                             text_color=MENU_TEXT,
                             anchor="w").pack(side="left", padx=14, pady=11)

            for r_idx, t in enumerate(teachers):
                row = ctk.CTkFrame(panel, fg_color="transparent")
                row.pack(fill="x")
                for value, w in [
                    (t.get("fio", "—"), 340),
                    (t.get("job_title") or "—", 240),
                    (t.get("clubs") or "—", 300),
                ]:
                    ctk.CTkLabel(row, text=value, width=w,
                                 font=("Inter", 13),
                                 text_color="#334155",
                                 anchor="w").pack(side="left", padx=14, pady=11)

                if r_idx < len(teachers) - 1:
                    ctk.CTkFrame(panel, height=1,
                                 fg_color="#F1F5F9").pack(fill="x")

        # Группа
        group = self.student.get("groups") or ""
        if not group:
            return

        groupmates = get_groupmates(group)

        panel2 = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                              corner_radius=12, border_width=1,
                              border_color=BORDER)
        panel2.pack(fill="x", pady=(0, 16))

        h2 = ctk.CTkFrame(panel2, fg_color="transparent")
        h2.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h2, text=f"Группа {group}",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel2, height=1, fg_color=BORDER).pack(fill="x")

        if not groupmates:
            ctk.CTkLabel(panel2, text="В группе нет студентов",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        hr = ctk.CTkFrame(panel2, fg_color="#F8FAFC", corner_radius=0)
        hr.pack(fill="x")
        for text, w in [("ФИО", 340), ("Номер студенческого", 240), ("Группа", 200)]:
            ctk.CTkLabel(hr, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, s in enumerate(groupmates):
            row = ctk.CTkFrame(panel2, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (s.get("fio", "—"), 340),
                (s.get("number") or "—", 240),
                (s.get("groups") or "—", 200),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(groupmates) - 1:
                ctk.CTkFrame(panel2, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # ПОРТФОЛИО
    # ============================================================

    def _show_portfolio(self):
        from logic.student import get_achievements

        ctk.CTkLabel(self.content, text="Портфолио",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Индивидуальные достижения и участие в олимпиадах",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.student:
            ctk.CTkLabel(self.content, text="Нет данных о студенте",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        achievements = get_achievements(self.student["id"])

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Мои достижения",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not achievements:
            ctk.CTkLabel(panel, text="Пока нет достижений",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=60)
            return

        hr = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        hr.pack(fill="x")
        for text, w in [("Название", 340), ("Тип", 160),
                        ("Уровень", 160), ("Дата", 140), ("Результат", 200)]:
            ctk.CTkLabel(hr, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, a in enumerate(achievements):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (a.get("title", "—"), 340),
                (a.get("type") or "—", 160),
                (a.get("level") or "—", 160),
                (a.get("date") or "—", 140),
                (a.get("result") or "—", 200),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(achievements) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")
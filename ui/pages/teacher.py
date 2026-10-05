"""
Панель преподавателя (Рисунки 5, 6, 8, 9, 10 из отчёта).

Единый фрейм со всеми страницами:
- Панель управления
- Журнал
- Посещаемость
- Достижения
- Расписание

Данные — из логики (logic/teacher.py и logic/student.py).
"""

import customtkinter as ctk
from ui.theme import (
    HEADER_BG, SIDEBAR_BG, CONTENT_BG, CARD_BG,
    TEXT_DARK, TEXT_GRAY, TEXT_BLUE, MENU_ACTIVE,
    MENU_TEXT, BORDER
)


# Ширины колонок для таблиц
COL_DATE = 140
COL_TIME = 150
COL_TOPIC = 320
COL_CLUB = 220
COL_ROOM = 120
COL_STUDENT = 300
COL_STATUS = 200
COL_GRADE = 100
COL_ACTION = 140
COL_TITLE = 340
COL_TYPE = 160
COL_LEVEL = 160
COL_RESULT = 200


class TeacherApp(ctk.CTkFrame):
    """Фрейм преподавателя со всеми страницами."""

    def __init__(self, parent, user, on_logout):
        super().__init__(parent, fg_color=CONTENT_BG)

        self.user = user
        self.on_logout = on_logout

        # Профиль преподавателя
        from logic.teacher import get_teacher_by_user_id
        self.teacher = get_teacher_by_user_id(user["id"])

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
                     text=f"{self.user.get('login', 'Преподаватель')}  •  Преподаватель",
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
            ("Журнал", "journal"),
            ("Посещаемость", "attendance"),
            ("Достижения", "achievements"),
            ("Расписание", "schedule"),
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
        elif page == "journal":
            self._show_journal()
        elif page == "attendance":
            self._show_attendance()
        elif page == "achievements":
            self._show_achievements()
        elif page == "schedule":
            self._show_schedule()

    # ============================================================
    # ПАНЕЛЬ УПРАВЛЕНИЯ
    # ============================================================

    def _show_dashboard(self):
        from logic.teacher import (
            get_teacher_clubs, get_teacher_students_count,
            get_teacher_lessons_count, get_teacher_attendance_rate,
            get_teacher_upcoming_lessons,
        )

        ctk.CTkLabel(self.content, text="Панель преподавателя",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        fio = f"{self.teacher['surname']} {self.teacher['name']}"
        if self.teacher.get("patronymic"):
            fio += f" {self.teacher['patronymic']}"

        ctk.CTkLabel(self.content,
                     text=f"{fio} — преподаватель",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        tid = self.teacher["id"]

        # Карточки
        clubs = get_teacher_clubs(tid)
        students = get_teacher_students_count(tid)
        lessons = get_teacher_lessons_count(tid)
        rate = get_teacher_attendance_rate(tid)

        cards = ctk.CTkFrame(self.content, fg_color="transparent")
        cards.pack(fill="x")

        for label, value in [
            ("МОИ КРУЖКИ", str(len(clubs))),
            ("СТУДЕНТОВ", str(students)),
            ("ЗАНЯТИЙ", str(lessons)),
            ("ПОСЕЩАЕМОСТЬ", f"{rate}%" if rate is not None else "—"),
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
        upcoming = get_teacher_upcoming_lessons(tid)

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

        if not upcoming:
            ctk.CTkLabel(panel, text="Нет занятий",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [("Дата", COL_DATE), ("Тема", COL_TOPIC),
                        ("Кружок", COL_CLUB), ("Аудитория", COL_ROOM)]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, lesson in enumerate(upcoming):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (lesson.get("date", "—"), COL_DATE),
                (lesson.get("topic", "—"), COL_TOPIC),
                (lesson.get("club_name", "—"), COL_CLUB),
                (lesson.get("room", "—"), COL_ROOM),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(upcoming) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # ЖУРНАЛ
    # ============================================================

    def _show_journal(self):
        from logic.teacher import get_teacher_clubs

        ctk.CTkLabel(self.content, text="Журнал",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        clubs = get_teacher_clubs(self.teacher["id"])

        if not clubs:
            ctk.CTkLabel(self.content,
                         text="Нет кружков",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        ctk.CTkLabel(self.content,
                     text=f"Мои кружки: {', '.join(c['name'] for c in clubs)}",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        # Показываем журнал первого кружка
        club = clubs[0]
        self._build_journal_for_club(club)

    def _build_journal_for_club(self, club):
        from logic.teacher import get_lessons_by_club, get_attendance_by_lesson

        lessons = get_lessons_by_club(club["id"])

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text=f"Журнал — {club['name']}",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not lessons:
            ctk.CTkLabel(panel, text="Нет занятий",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [("Дата", COL_DATE), ("Тема", COL_TOPIC),
                        ("Тип", 120), ("Часы", 100)]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, lesson in enumerate(lessons):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (lesson.get("date", "—"), COL_DATE),
                (lesson.get("topic", "—"), COL_TOPIC),
                (lesson.get("type") or "—", 120),
                (str(lesson.get("hours") or "—"), 100),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(lessons) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # ПОСЕЩАЕМОСТЬ
    # ============================================================

    def _show_attendance(self):
        from logic.teacher import (
            get_teacher_clubs, get_lessons_by_club,
            get_attendance_by_lesson,
        )

        ctk.CTkLabel(self.content, text="Посещаемость",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        clubs = get_teacher_clubs(self.teacher["id"])

        if not clubs:
            ctk.CTkLabel(self.content,
                         text="Нет кружков",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        ctk.CTkLabel(self.content,
                     text=f"Последнее занятие - {clubs[0]['name']}",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        # Последнее занятие первого кружка
        lessons = get_lessons_by_club(clubs[0]["id"])
        if not lessons:
            ctk.CTkLabel(self.content,
                         text="Нет занятий",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        lesson = lessons[-1]
        attendance = get_attendance_by_lesson(lesson["id"])

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h,
                     text=f"{lesson['date']} — {lesson['topic']}",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not attendance:
            ctk.CTkLabel(panel, text="Нет записей о посещаемости",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [("Студент", COL_STUDENT),
                        ("Статус", COL_STATUS), ("Действие", COL_ACTION)]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, a in enumerate(attendance):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")

            ctk.CTkLabel(row, text=a.get("student_fio", "—"),
                         width=COL_STUDENT,
                         font=("Inter", 13),
                         text_color="#334155",
                         anchor="w").pack(side="left", padx=14, pady=11)

            status = a.get("status") or "—"
            ctk.CTkLabel(row, text=status, width=COL_STATUS,
                         font=("Inter", 13),
                         text_color=self._status_color(status),
                         anchor="w").pack(side="left", padx=14, pady=11)

            ctk.CTkLabel(row, text="—", width=COL_ACTION,
                         font=("Inter", 13),
                         text_color="#94A3B8",
                         anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(attendance) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    def _status_color(self, status):
        return {
            "Присутствовал": "#166534",
            "Отсутствовал": "#991B1B",
            "Опоздал": "#854D0E",
        }.get(status, "#475569")

    # ============================================================
    # ДОСТИЖЕНИЯ
    # ============================================================

    def _show_achievements(self):
        from logic.teacher import get_teacher_students_achievements

        ctk.CTkLabel(self.content, text="Достижения учащихся",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Достижения ваших студентов",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            return

        achievements = get_teacher_students_achievements(self.teacher["id"])

        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Список достижений",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not achievements:
            ctk.CTkLabel(panel, text="Пока нет достижений",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=60)
            return

        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [("Студент", 240), ("Название", COL_TITLE),
                        ("Тип", COL_TYPE), ("Уровень", COL_LEVEL),
                        ("Дата", 140), ("Результат", COL_RESULT)]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        for r_idx, a in enumerate(achievements):
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x")
            for value, w in [
                (a.get("student_fio", "-"), 240),
                (a.get("title", "-"), COL_TITLE),
                (a.get("type") or "-", COL_TYPE),
                (a.get("level") or "-", COL_LEVEL),
                (a.get("date") or "-", 140),
                (a.get("result") or "-", COL_RESULT),
            ]:
                ctk.CTkLabel(row, text=value, width=w,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(achievements) - 1:
                ctk.CTkFrame(panel, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    # ============================================================
    # РАСПИСАНИЕ
    # ============================================================

    def _show_schedule(self):
        from logic.teacher import get_teacher_schedule

        ctk.CTkLabel(self.content, text="Расписание",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Ваши занятия на неделю",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            return

        schedule = get_teacher_schedule(self.teacher["id"])
        total = sum(len(ls) for ls in schedule.values())

        if total == 0:
            ctk.CTkLabel(self.content,
                         text="Расписание не составлено",
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
                             anchor="w").pack(fill="x", padx=10, pady=(0, 8))
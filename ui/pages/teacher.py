"""
Панель преподавателя (Рисунки 5, 6, 8, 9, 10 из отчёта).

Единый фрейм со всеми страницами:
- Панель управления
- Мои кружки
- Журнал (таблица студентов × занятия, редактирование оценок)
- Посещаемость
- Достижения
- Расписание
"""

import customtkinter as ctk
from tkinter import messagebox
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
            ("Мои кружки", "clubs"),
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
        elif page == "clubs":
            self._show_clubs()
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
    # МОИ КРУЖКИ
    # ============================================================

    def _show_clubs(self):
        from logic.teacher import get_teacher_clubs_full

        ctk.CTkLabel(self.content, text="Мои кружки",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Кружки и секции, которые вы ведёте",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        clubs = get_teacher_clubs_full(self.teacher["id"])

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
            ctk.CTkLabel(panel, text="У вас нет кружков",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        columns = [
            ("Название", 240),
            ("Тип", 140),
            ("Расписание", 280),
            ("Аудитория", 120),
            ("Действия", 280),
        ]

        # Заголовки
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

        # Прокрутка
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent",
                                        scrollbar_button_color="#CBD5E1")
        scroll.pack(fill="both", expand=True)

        for r_idx, c in enumerate(clubs):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x")

            for col_idx, (_, width) in enumerate(columns):
                row.grid_columnconfigure(col_idx, weight=0, minsize=width)

            values = [
                c.get("name", "—"),
                c.get("type") or "—",
                c.get("schedule") or "—",
                c.get("room") or "—",
            ]

            for col_idx, value in enumerate(values):
                ctk.CTkLabel(row, text=value,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").grid(
                    row=0, column=col_idx,
                    sticky="w", padx=14, pady=11
                )

            # Действия
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=4, sticky="w", padx=14, pady=11)

            ctk.CTkButton(actions, text="студенты",
                          fg_color="#DBEAFE", hover_color="#BFDBFE",
                          text_color="#1E40AF",
                          width=80, height=28,
                          command=lambda club=c: self._on_manage_students(club)
                          ).pack(side="left", padx=(0, 4))

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
        dialog = TeacherClubDialog(
            self,
            teacher_id=self.teacher["id"],
            on_success=self._reload_clubs,
            club=None
        )
        dialog.grab_set()

    def _on_edit_club(self, club):
        """Открыть модалку редактирования."""
        dialog = TeacherClubDialog(
            self,
            teacher_id=self.teacher["id"],
            on_success=self._reload_clubs,
            club=club
        )
        dialog.grab_set()

    def _on_delete_club(self, club_id, club_name):
        """Удалить кружок."""
        from logic.teacher import delete_teacher_club

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить кружок «{club_name}»?"
        )

        if not confirm:
            return

        if delete_teacher_club(club_id, self.teacher["id"]):
            messagebox.showinfo("Успех", "Кружок удалён")
            self._reload_clubs()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    def _reload_clubs(self):
        """Перезагрузить страницу кружков."""
        self.show_page("clubs")

    def _on_manage_students(self, club):
        """Открыть модалку управления студентами кружка."""
        dialog = ManageStudentsDialog(
            self,
            club=club,
            on_success=self._reload_clubs
        )
        dialog.grab_set()

    # ============================================================
    # ЖУРНАЛ
    # ============================================================

    def _show_journal(self):
        """Журнал оценок — таблица студентов × занятия."""
        from logic.teacher import get_teacher_clubs_full

        ctk.CTkLabel(self.content, text="Журнал",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Выставление и редактирование оценок",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        clubs = get_teacher_clubs_full(self.teacher["id"])

        if not clubs:
            ctk.CTkLabel(self.content,
                         text="Нет кружков",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        # --- Верхняя панель ---
        top = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                           corner_radius=12, border_width=1,
                           border_color=BORDER)
        top.pack(fill="x", pady=(0, 16))

        top_inner = ctk.CTkFrame(top, fg_color="transparent")
        top_inner.pack(fill="x", padx=22, pady=16)

        ctk.CTkLabel(top_inner, text="Кружок:",
                     font=("Inter", 13, "bold"),
                     text_color=TEXT_DARK).pack(side="left", padx=(0, 8))

        self._journal_clubs = clubs
        club_names = [c["name"] for c in clubs]
        self._journal_club_var = ctk.StringVar(value=club_names[0])

        club_menu = ctk.CTkOptionMenu(
            top_inner,
            values=club_names,
            variable=self._journal_club_var,
            fg_color="#F8FAFC",
            button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=36, corner_radius=8,
            width=250,
            command=lambda _: self._reload_journal_table()
        )
        club_menu.pack(side="left", padx=(0, 16))

        ctk.CTkButton(
            top_inner, text="+ Добавить занятие",
            fg_color="#2563EB", hover_color="#1D4ED8",
            height=36, corner_radius=8,
            font=("Inter", 13, "bold"),
            command=self._on_add_lesson
        ).pack(side="right")

        # --- Контейнер для таблицы ---
        self._journal_table_frame = ctk.CTkFrame(self.content,
                                                  fg_color="transparent")
        self._journal_table_frame.pack(fill="both", expand=True)

        self._reload_journal_table()

    def _reload_journal_table(self):
        """Перерисовать таблицу журнала."""
        from logic.teacher import (
            get_students_by_club,
            get_lessons_by_club_sorted,
            get_attendance_map,
            get_student_averages,
        )

        for w in self._journal_table_frame.winfo_children():
            w.destroy()

        club_name = self._journal_club_var.get()
        club = next((c for c in self._journal_clubs
                     if c["name"] == club_name), None)
        if not club:
            return

        students = get_students_by_club(club["id"])
        lessons = get_lessons_by_club_sorted(club["id"])
        attendance = get_attendance_map(club["id"])
        averages = get_student_averages(club["id"])

        if not students:
            ctk.CTkLabel(self._journal_table_frame,
                         text="В кружке нет студентов",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        if not lessons:
            ctk.CTkLabel(self._journal_table_frame,
                         text="Нет занятий. Нажмите «+ Добавить занятие»",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        panel = ctk.CTkFrame(self._journal_table_frame, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        h_scroll = ctk.CTkScrollableFrame(
            panel,
            orientation="horizontal",
            fg_color="transparent",
            scrollbar_button_color="#CBD5E1",
            height=520
        )
        h_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        COL_STUDENT = 240
        COL_DATE = 100
        COL_AVG = 110
        COL_FINAL = 100

        table = ctk.CTkFrame(h_scroll, fg_color="transparent")
        table.pack(fill="both", expand=True)

        # --- Заголовки ---
        table.grid_columnconfigure(0, weight=0, minsize=COL_STUDENT)

        head_student = ctk.CTkFrame(table, fg_color="#F8FAFC",
                                     corner_radius=0)
        head_student.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(head_student, text="Студент",
                     font=("Inter", 12, "bold"),
                     text_color=MENU_TEXT,
                     anchor="w").pack(fill="x", padx=14, pady=11)

        for col_idx, lesson in enumerate(lessons, start=1):
            table.grid_columnconfigure(col_idx, weight=0, minsize=COL_DATE)
            date_str = self._format_date_short(lesson.get("date", ""))

            head_date = ctk.CTkFrame(table, fg_color="#F8FAFC",
                                      corner_radius=0)
            head_date.grid(row=0, column=col_idx, sticky="nsew")
            ctk.CTkLabel(head_date, text=date_str,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="center").pack(fill="x", padx=4, pady=11)

        # Колонки «Средний» и «Итог»
        col_avg = len(lessons) + 1
        col_final = len(lessons) + 2

        table.grid_columnconfigure(col_avg, weight=0, minsize=COL_AVG)
        table.grid_columnconfigure(col_final, weight=0, minsize=COL_FINAL)

        head_avg = ctk.CTkFrame(table, fg_color="#F8FAFC", corner_radius=0)
        head_avg.grid(row=0, column=col_avg, sticky="nsew")
        ctk.CTkLabel(head_avg, text="Средний",
                     font=("Inter", 12, "bold"),
                     text_color=MENU_TEXT,
                     anchor="center").pack(fill="x", padx=4, pady=11)

        head_final = ctk.CTkFrame(table, fg_color="#F8FAFC", corner_radius=0)
        head_final.grid(row=0, column=col_final, sticky="nsew")
        ctk.CTkLabel(head_final, text="Итог",
                     font=("Inter", 12, "bold"),
                     text_color=MENU_TEXT,
                     anchor="center").pack(fill="x", padx=4, pady=11)

        # --- Данные ---
        for r_idx, student in enumerate(students, start=1):
            cell_student = ctk.CTkFrame(table, fg_color="transparent")
            cell_student.grid(row=r_idx, column=0, sticky="nsew")
            ctk.CTkLabel(cell_student, text=student.get("fio", "—"),
                         font=("Inter", 13),
                         text_color="#334155",
                         anchor="w").pack(fill="x", padx=14, pady=8)

            for col_idx, lesson in enumerate(lessons, start=1):
                key = (student["id"], lesson["id"])
                info = attendance.get(key)

                grade = info["grade"] if info else None
                status = info["status"] if info else None
                comment = info.get("comment") if info else None

                bg, text_color = self._cell_color(grade, status)

                if grade is not None:
                    text = str(grade)
                else:
                    text = "—"

                if comment:
                    text += " *"

                cell = ctk.CTkFrame(table, fg_color="transparent")
                cell.grid(row=r_idx, column=col_idx, sticky="nsew")

                ctk.CTkButton(
                    cell, text=text,
                    fg_color=bg, hover_color=bg,
                    text_color=text_color,
                    width=70, height=36,
                    corner_radius=6,
                    font=("Inter", 13, "bold"),
                    command=lambda s=student, l=lesson:
                        self._on_edit_grade(s, l)
                ).pack(padx=8, pady=6)

            # Средний
            info_avg = averages.get(student["id"])
            avg_text = f"{info_avg['avg']:.1f}" if info_avg else "—"

            cell_avg = ctk.CTkFrame(table, fg_color="transparent")
            cell_avg.grid(row=r_idx, column=col_avg, sticky="nsew")
            ctk.CTkLabel(cell_avg, text=avg_text,
                         font=("Inter", 13, "bold"),
                         text_color="#1E293B",
                         anchor="center").pack(fill="x", padx=8, pady=8)

            # Итог
            final_text = str(info_avg["final"]) if info_avg else "—"

            cell_final = ctk.CTkFrame(table, fg_color="transparent")
            cell_final.grid(row=r_idx, column=col_final, sticky="nsew")
            ctk.CTkLabel(cell_final, text=final_text,
                         font=("Inter", 13, "bold"),
                         text_color="#1E293B",
                         anchor="center").pack(fill="x", padx=8, pady=8)

    def _format_date_short(self, date_str):
        """2026-10-15 → 15.10"""
        if not date_str:
            return "—"
        parts = date_str.split("-")
        if len(parts) >= 3:
            return f"{parts[2]}.{parts[1]}"
        return date_str

    def _cell_color(self, grade, status):
        """Цвет ячейки."""
        if grade == 5:
            return "#DCFCE7", "#166534"
        elif grade == 4:
            return "#DBEAFE", "#1E40AF"
        elif grade == 3:
            return "#FEF9C3", "#854D0E"
        elif grade == 2:
            return "#FEE2E2", "#991B1B"
        elif status == "Отсутствовал":
            return "#F1F5F9", "#94A3B8"
        else:
            return "#FFFFFF", "#94A3B8"

    def _on_edit_grade(self, student, lesson):
        """Открыть модалку редактирования оценки."""
        dialog = EditGradeDialog(
            self,
            student=student,
            lesson=lesson,
            on_success=self._reload_journal_table
        )
        dialog.grab_set()

    def _on_add_lesson(self):
        """Открыть модалку добавления занятия."""
        club_name = self._journal_club_var.get()
        club = next((c for c in self._journal_clubs
                     if c["name"] == club_name), None)
        if not club:
            return

        dialog = AddLessonDialog(
            self,
            club=club,
            on_success=self._reload_journal_table
        )
        dialog.grab_set()

    # ============================================================
    # ПОСЕЩАЕМОСТЬ
    # ============================================================

    def _show_attendance(self):
        """Посещаемость — выбор занятия + прокрутка."""
        from logic.teacher import get_teacher_clubs_full

        ctk.CTkLabel(self.content, text="Посещаемость",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Отметка посещаемости по занятиям",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        clubs = get_teacher_clubs_full(self.teacher["id"])

        if not clubs:
            ctk.CTkLabel(self.content,
                         text="Нет кружков",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        # --- Верхняя панель: выбор кружка ---
        top = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                           corner_radius=12, border_width=1,
                           border_color=BORDER)
        top.pack(fill="x", pady=(0, 16))

        top_inner = ctk.CTkFrame(top, fg_color="transparent")
        top_inner.pack(fill="x", padx=22, pady=16)

        ctk.CTkLabel(top_inner, text="Кружок:",
                     font=("Inter", 13, "bold"),
                     text_color=TEXT_DARK).pack(side="left", padx=(0, 8))

        self._att_clubs = clubs
        club_names = [c["name"] for c in clubs]
        self._att_club_var = ctk.StringVar(value=club_names[0])

        ctk.CTkOptionMenu(
            top_inner,
            values=club_names,
            variable=self._att_club_var,
            fg_color="#F8FAFC",
            button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=36, corner_radius=8,
            width=250,
            command=lambda _: self._reload_attendance_lessons()
        ).pack(side="left")

        # --- Контейнер для выбора занятия ---
        self._att_lessons_frame = ctk.CTkFrame(self.content,
                                                fg_color="transparent")
        self._att_lessons_frame.pack(fill="x", pady=(0, 16))

        # --- Контейнер для таблицы ---
        self._att_table_frame = ctk.CTkFrame(self.content,
                                              fg_color="transparent")
        self._att_table_frame.pack(fill="both", expand=True)

        # Загружаем занятия первого кружка
        self._reload_attendance_lessons()

    def _reload_attendance_lessons(self):
        """Перерисовать панель выбора занятия и таблицу."""
        for w in self._att_lessons_frame.winfo_children():
            w.destroy()
        for w in self._att_table_frame.winfo_children():
            w.destroy()

        from logic.teacher import get_lessons_by_club_sorted

        club_name = self._att_club_var.get()
        club = next((c for c in self._att_clubs
                     if c["name"] == club_name), None)
        if not club:
            return

        lessons = get_lessons_by_club_sorted(club["id"])

        if not lessons:
            ctk.CTkLabel(self._att_lessons_frame,
                         text="Нет занятий для этого кружка",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=20)
            return

        # --- Панель выбора занятия ---
        lesson_panel = ctk.CTkFrame(self._att_lessons_frame,
                                     fg_color=CARD_BG,
                                     corner_radius=12,
                                     border_width=1,
                                     border_color=BORDER)
        lesson_panel.pack(fill="x")

        lesson_inner = ctk.CTkFrame(lesson_panel, fg_color="transparent")
        lesson_inner.pack(fill="x", padx=22, pady=16)

        ctk.CTkLabel(lesson_inner, text="Занятие:",
                     font=("Inter", 13, "bold"),
                     text_color=TEXT_DARK).pack(side="left", padx=(0, 8))

        # Формируем список занятий: "15.10.2026 — Сборка манипулятора"
        self._att_lessons = lessons
        lesson_labels = [
            f"{l.get('date', '')} — {l.get('topic', '')}"
            for l in lessons
        ]

        # По умолчанию — последнее
        self._att_lesson_var = ctk.StringVar(value=lesson_labels[-1])

        ctk.CTkOptionMenu(
            lesson_inner,
            values=lesson_labels,
            variable=self._att_lesson_var,
            fg_color="#F8FAFC",
            button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=36, corner_radius=8,
            width=400,
            command=lambda _: self._reload_attendance_table()
        ).pack(side="left")

        # Загружаем таблицу выбранного занятия
        self._reload_attendance_table()

    def _reload_attendance_table(self):
        """Перерисовать таблицу посещаемости выбранного занятия."""
        from logic.teacher import get_attendance_by_lesson

        for w in self._att_table_frame.winfo_children():
            w.destroy()

        lesson_label = self._att_lesson_var.get()
        # Ищем занятие по метке
        lesson = None
        for l in self._att_lessons:
            if f"{l.get('date', '')} — {l.get('topic', '')}" == lesson_label:
                lesson = l
                break

        if not lesson:
            return

        attendance = get_attendance_by_lesson(lesson["id"])

        panel = ctk.CTkFrame(self._att_table_frame, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        # Заголовок
        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h,
                     text=f"{lesson.get('date', '')} — {lesson.get('topic', '')}",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not attendance:
            ctk.CTkLabel(panel,
                         text="Нет записей о посещаемости для этого занятия",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=40)
            return

        # Заголовки таблицы
        head = ctk.CTkFrame(panel, fg_color="#F8FAFC", corner_radius=0)
        head.pack(fill="x")
        for text, w in [
            ("Студент", COL_STUDENT),
            ("Статус", COL_STATUS),
            ("Оценка", COL_GRADE),
            ("Примечание", 300),
        ]:
            ctk.CTkLabel(head, text=text, width=w,
                         font=("Inter", 12, "bold"),
                         text_color=MENU_TEXT,
                         anchor="w").pack(side="left", padx=14, pady=11)

        # Прокрутка
        scroll = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
            corner_radius=0
        )
        scroll.pack(fill="both", expand=True)

        for r_idx, a in enumerate(attendance):
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x")

            # Студент
            ctk.CTkLabel(row, text=a.get("student_fio", "—"),
                         width=COL_STUDENT,
                         font=("Inter", 13),
                         text_color="#334155",
                         anchor="w").pack(side="left", padx=14, pady=11)

            # Статус
            status = a.get("status") or "—"
            ctk.CTkLabel(row, text=status, width=COL_STATUS,
                         font=("Inter", 13),
                         text_color=self._status_color(status),
                         anchor="w").pack(side="left", padx=14, pady=11)

            # Оценка
            grade = a.get("grade")
            grade_text = str(grade) if grade is not None else "—"
            ctk.CTkLabel(row, text=grade_text, width=COL_GRADE,
                         font=("Inter", 13, "bold"),
                         text_color="#1E293B",
                         anchor="w").pack(side="left", padx=14, pady=11)

            # Примечание
            comment = a.get("comment") or "—"
            ctk.CTkLabel(row, text=comment, width=300,
                         font=("Inter", 13),
                         text_color="#94A3B8",
                         anchor="w").pack(side="left", padx=14, pady=11)

            if r_idx < len(attendance) - 1:
                ctk.CTkFrame(scroll, height=1,
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
        """Достижения студентов — с горизонтальной прокруткой."""
        from logic.teacher import get_teacher_students_achievements_full

        ctk.CTkLabel(self.content, text="Достижения учащихся",
                     font=("Inter", 22, "bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x")

        ctk.CTkLabel(self.content,
                     text="Достижения ваших студентов",
                     font=("Inter", 13), text_color=TEXT_GRAY,
                     anchor="w").pack(fill="x", pady=(4, 24))

        if not self.teacher:
            ctk.CTkLabel(self.content,
                         text="Нет данных о преподавателе",
                         font=("Inter", 16),
                         text_color="#94A3B8").pack(pady=60)
            return

        achievements = get_teacher_students_achievements_full(self.teacher["id"])

        # --- Панель ---
        panel = ctk.CTkFrame(self.content, fg_color=CARD_BG,
                             corner_radius=12, border_width=1,
                             border_color=BORDER)
        panel.pack(fill="both", expand=True)

        # Заголовок панели
        h = ctk.CTkFrame(panel, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=16)
        ctk.CTkLabel(h, text="Список достижений",
                     font=("Inter", 15, "bold"),
                     text_color=TEXT_DARK).pack(side="left")

        ctk.CTkButton(h, text="+ Добавить достижение",
                      fg_color="#2563EB", hover_color="#1D4ED8",
                      height=32, corner_radius=8,
                      font=("Inter", 12, "bold"),
                      command=self._on_add_achievement).pack(side="right")

        ctk.CTkFrame(panel, height=1, fg_color=BORDER).pack(fill="x")

        if not achievements:
            ctk.CTkLabel(panel, text="Пока нет достижений",
                         font=("Inter", 14),
                         text_color="#94A3B8").pack(pady=60)
            return

        # === ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА ===
        h_scroll = ctk.CTkScrollableFrame(
            panel,
            orientation="horizontal",
            fg_color="transparent",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
            corner_radius=0,
            height=520
        )
        h_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # Колонки
        COL_STUDENT = 240
        COL_TITLE = 340
        COL_TYPE = 160
        COL_LEVEL = 160
        COL_DATE = 140
        COL_RESULT = 200
        COL_ACTION = 120

        table = ctk.CTkFrame(h_scroll, fg_color="transparent")
        table.pack(fill="both", expand=True)

        # === Заголовки ===
        columns = [
            ("Студент", COL_STUDENT),
            ("Название", COL_TITLE),
            ("Тип", COL_TYPE),
            ("Уровень", COL_LEVEL),
            ("Дата", COL_DATE),
            ("Результат", COL_RESULT),
            ("Действия", COL_ACTION),
        ]

        head = ctk.CTkFrame(table, fg_color="#F8FAFC", corner_radius=0)
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

        # === Данные ===
        for r_idx, a in enumerate(achievements):
            row = ctk.CTkFrame(table, fg_color="transparent")
            row.pack(fill="x")

            for col_idx, (_, width) in enumerate(columns):
                row.grid_columnconfigure(col_idx, weight=0, minsize=width)

            values = [
                a.get("student_fio", "—"),
                a.get("title", "—"),
                a.get("type") or "—",
                a.get("level") or "—",
                a.get("date") or "—",
                a.get("result") or "—",
            ]

            for col_idx, value in enumerate(values):
                ctk.CTkLabel(row, text=value,
                             font=("Inter", 13),
                             text_color="#334155",
                             anchor="w").grid(
                    row=0, column=col_idx,
                    sticky="w", padx=14, pady=11
                )

            # Кнопка «удалить»
            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=len(values),
                         sticky="w", padx=14, pady=11)

            ctk.CTkButton(actions, text="удалить",
                          fg_color="#FEE2E2", hover_color="#FECACA",
                          text_color="#991B1B",
                          width=80, height=28,
                          command=lambda aid=a.get("id"),
                                         atitle=a.get("title"):
                              self._on_delete_achievement(aid, atitle)
                          ).pack(side="left")

            if r_idx < len(achievements) - 1:
                ctk.CTkFrame(table, height=1,
                             fg_color="#F1F5F9").pack(fill="x")

    def _on_add_achievement(self):
        """Открыть модалку добавления достижения."""
        dialog = AddAchievementDialog(
            self,
            teacher_id=self.teacher["id"],
            on_success=self._reload_achievements
        )
        dialog.grab_set()

    def _on_delete_achievement(self, achievement_id, title):
        """Удалить достижение."""
        from logic.teacher import delete_achievement

        confirm = messagebox.askyesno(
            "Подтверждение",
            f"Удалить достижение «{title}»?"
        )

        if not confirm:
            return

        if delete_achievement(achievement_id):
            messagebox.showinfo("Успех", "Достижение удалено")
            self._reload_achievements()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить")

    def _reload_achievements(self):
        """Перезагрузить страницу достижений."""
        self.show_page("achievements")

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


# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВЛЕНИЕ / РЕДАКТИРОВАНИЕ КРУЖКА
# ============================================================

class TeacherClubDialog(ctk.CTkToplevel):
    """Модалка добавления/редактирования кружка преподавателем."""

    def __init__(self, parent, teacher_id, on_success, club=None):
        super().__init__(parent)

        self.teacher_id = teacher_id
        self.on_success = on_success
        self.club = club
        self.is_edit = club is not None

        self.title("Редактировать кружок" if self.is_edit else "Добавить кружок")
        self.geometry("500x560")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=36, pady=28)

        title = "Редактировать кружок" if self.is_edit else "Добавить кружок"
        ctk.CTkLabel(card, text=title,
                     font=("Inter", 20, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 24))

        self.name_entry = self._add_field(card, "Название", "Робототехника")

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

        self.schedule_entry = self._add_field(
            card, "Расписание", "Пн 15:00-16:30, Ср 15:00-16:30"
        )
        self.room_entry = self._add_field(card, "Аудитория", "204")

        if self.is_edit:
            self.name_entry.insert(0, club.get("name") or "")
            self.type_var.set(club.get("type") or "Кружок")
            self.schedule_entry.insert(0, club.get("schedule") or "")
            self.room_entry.insert(0, club.get("room") or "")

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
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
        from logic.teacher import create_teacher_club, update_teacher_club

        name = self.name_entry.get().strip()
        type_ = self.type_var.get()
        schedule = self.schedule_entry.get().strip()
        room = self.room_entry.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Введите название")
            return

        if not schedule:
            messagebox.showwarning("Ошибка", "Введите расписание")
            return

        if self.is_edit:
            success = update_teacher_club(
                self.club["id"], self.teacher_id,
                name, type_, schedule, room
            )
        else:
            success = create_teacher_club(
                self.teacher_id, name, type_, schedule, room
            )

        if success:
            messagebox.showinfo("Успех",
                                "Кружок обновлён" if self.is_edit
                                else "Кружок создан")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")


# ============================================================
# МОДАЛЬНОЕ ОКНО: УПРАВЛЕНИЕ СТУДЕНТАМИ КРУЖКА
# ============================================================

class ManageStudentsDialog(ctk.CTkToplevel):
    """Модалка выбора студентов для кружка."""

    def __init__(self, parent, club, on_success):
        super().__init__(parent)

        self.club = club
        self.on_success = on_success

        self.title(f"Студенты — {club.get('name', '')}")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=28, pady=24)

        ctk.CTkLabel(card,
                     text=f"Студенты кружка «{club.get('name', '')}»",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x")

        ctk.CTkLabel(card,
                     text="Отметьте студентов, которые должны быть записаны",
                     font=("Inter", 12),
                     text_color="#64748B",
                     anchor="w").pack(fill="x", pady=(4, 16))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._filter_students())

        search_entry = ctk.CTkEntry(
            card, placeholder_text="Поиск по ФИО или группе",
            textvariable=self.search_var,
            fg_color="#F8FAFC", border_color="#CBD5E1",
            font=("Inter", 13), height=38, corner_radius=8
        )
        search_entry.pack(fill="x", pady=(0, 16))

        from logic.teacher import get_all_students, get_enrolled_students

        self.all_students = get_all_students()
        enrolled = set(get_enrolled_students(club["id"]))

        self.checkboxes = {}

        scroll = ctk.CTkScrollableFrame(
            card, fg_color="#F8FAFC",
            scrollbar_button_color="#CBD5E1",
            corner_radius=8
        )
        scroll.pack(fill="both", expand=True, pady=(0, 16))

        self.scroll = scroll

        for s in self.all_students:
            self._build_student_row(scroll, s, s["id"] in enrolled)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x")

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Сохранить",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_save
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _build_student_row(self, parent, student, is_enrolled):
        row = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=6)
        row.pack(fill="x", padx=6, pady=3)

        var = ctk.BooleanVar(value=is_enrolled)
        self.checkboxes[student["id"]] = var

        ctk.CTkCheckBox(
            row, text="",
            variable=var,
            width=24,
            checkbox_width=22, checkbox_height=22,
            corner_radius=4,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        ).pack(side="left", padx=(12, 8), pady=10)

        ctk.CTkLabel(row, text=student.get("fio", "—"),
                     font=("Inter", 13),
                     text_color="#334155",
                     anchor="w").pack(side="left", fill="x",
                                      expand=True, pady=10)

        ctk.CTkLabel(row, text=student.get("groups") or "—",
                     font=("Inter", 12),
                     text_color="#94A3B8",
                     anchor="e",
                     width=100).pack(side="right", padx=(8, 12), pady=10)

    def _filter_students(self):
        query = self.search_var.get().strip().lower()

        for w in self.scroll.winfo_children():
            w.destroy()

        from logic.teacher import get_enrolled_students
        enrolled = set(get_enrolled_students(self.club["id"]))

        for s in self.all_students:
            fio = (s.get("fio") or "").lower()
            group = (s.get("groups") or "").lower()

            if query and query not in fio and query not in group:
                continue

            is_enrolled = s["id"] in enrolled
            if s["id"] in self.checkboxes:
                is_enrolled = self.checkboxes[s["id"]].get()

            self._build_student_row(self.scroll, s, is_enrolled)

    def _on_save(self):
        from logic.teacher import save_club_enrollments

        selected = [
            sid for sid, var in self.checkboxes.items()
            if var.get()
        ]

        if save_club_enrollments(self.club["id"], selected):
            messagebox.showinfo("Успех",
                                f"Записано студентов: {len(selected)}")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")


# ============================================================
# МОДАЛЬНОЕ ОКНО: РЕДАКТИРОВАНИЕ ОЦЕНКИ
# ============================================================

class EditGradeDialog(ctk.CTkToplevel):
    """Модалка редактирования оценки."""

    def __init__(self, parent, student, lesson, on_success):
        super().__init__(parent)

        self.student = student
        self.lesson = lesson
        self.on_success = on_success

        self.title("Оценка")
        self.geometry("420x500")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(card, text="Редактировать оценку",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x")

        ctk.CTkLabel(card, text=f"{student.get('fio', '—')}",
                     font=("Inter", 14),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(8, 2))

        ctk.CTkLabel(card,
                     text=f"{lesson.get('date', '—')} — {lesson.get('topic', '')}",
                     font=("Inter", 12),
                     text_color="#64748B",
                     anchor="w").pack(fill="x", pady=(0, 20))

        current = self._get_current_attendance(student["id"], lesson["id"])
        current_grade = current.get("grade") if current else None
        current_status = (current.get("status") if current
                          else "Присутствовал")
        current_comment = (current.get("comment") if current else "")

        # Оценка
        ctk.CTkLabel(card, text="Оценка",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 6))

        grades_frame = ctk.CTkFrame(card, fg_color="transparent")
        grades_frame.pack(fill="x", pady=(0, 16))

        self.grade_var = ctk.IntVar(value=current_grade or 0)
        self.grade_buttons = {}

        for grade in [2, 3, 4, 5]:
            btn = ctk.CTkButton(
                grades_frame, text=str(grade),
                width=70, height=50,
                corner_radius=8,
                font=("Inter", 18, "bold"),
                command=lambda g=grade: self._select_grade(g)
            )
            btn.pack(side="left", padx=(0, 8))
            self.grade_buttons[grade] = btn

        ctk.CTkButton(
            grades_frame, text="Сброс",
            fg_color="transparent", border_width=1,
            border_color="#CBD5E1", text_color="#475569",
            hover_color="#F1F5F9",
            width=70, height=50, corner_radius=8,
            font=("Inter", 13),
            command=self._reset_grade
        ).pack(side="left")

        # Статус
        ctk.CTkLabel(card, text="Посещаемость",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 6))

        self.status_var = ctk.StringVar(value=current_status)
        ctk.CTkOptionMenu(
            card,
            values=["Присутствовал", "Отсутствовал", "Опоздал"],
            variable=self.status_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13),
            height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 16))

        # Примечание
        ctk.CTkLabel(card, text="Примечание",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 6))

        self.comment_entry = ctk.CTkEntry(
            card, placeholder_text="необязательно",
            fg_color="#F8FAFC", border_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        )
        self.comment_entry.pack(fill="x", pady=(0, 20))
        if current_comment:
            self.comment_entry.insert(0, current_comment)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x")

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Сохранить",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_save
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        if current_grade:
            self._select_grade(current_grade)

    def _get_current_attendance(self, student_id, lesson_id):
        from db.database import get_connection

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, grade, status, comment
                FROM attendance
                WHERE student_id = ? AND lesson_id = ?
            """, (student_id, lesson_id))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def _select_grade(self, grade):
        self.grade_var.set(grade)

        colors = {
            5: ("#DCFCE7", "#166534"),
            4: ("#DBEAFE", "#1E40AF"),
            3: ("#FEF9C3", "#854D0E"),
            2: ("#FEE2E2", "#991B1B"),
        }

        for g, btn in self.grade_buttons.items():
            if g == grade:
                bg, fg = colors[g]
                btn.configure(fg_color=bg, text_color=fg,
                              border_width=2, border_color=fg)
            else:
                btn.configure(fg_color="#F8FAFC", text_color="#475569",
                              border_width=1, border_color="#CBD5E1")

    def _reset_grade(self):
        self.grade_var.set(0)
        for btn in self.grade_buttons.values():
            btn.configure(fg_color="#F8FAFC", text_color="#475569",
                          border_width=1, border_color="#CBD5E1")

    def _on_save(self):
        from logic.teacher import update_grade

        grade = self.grade_var.get()
        if grade == 0:
            grade = None

        status = self.status_var.get()
        comment = self.comment_entry.get().strip()

        if update_grade(self.lesson["id"], self.student["id"],
                        grade, comment, status):
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")


# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВЛЕНИЕ ЗАНЯТИЯ
# ============================================================

class AddLessonDialog(ctk.CTkToplevel):
    """Модалка добавления занятия."""

    def __init__(self, parent, club, on_success):
        super().__init__(parent)

        self.club = club
        self.on_success = on_success

        self.title("Добавить занятие")
        self.geometry("460x520")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        card = ctk.CTkFrame(self, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=32, pady=24)

        ctk.CTkLabel(card, text="Добавить занятие",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(card, text=f"Кружок: {club.get('name', '')}",
                     font=("Inter", 12),
                     text_color="#64748B",
                     anchor="w").pack(fill="x", pady=(0, 20))

        self.date_entry = self._add_field(card, "Дата (ГГГГ-ММ-ДД)", "2026-10-25")
        self.topic_entry = self._add_field(card, "Тема занятия", "Сборка робота")

        ctk.CTkLabel(card, text="Тип",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.type_var = ctk.StringVar(value="Практика")
        ctk.CTkOptionMenu(
            card, values=["Практика", "Теория", "Лабораторная", "Семинар"],
            variable=self.type_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        self.hours_entry = self._add_field(card, "Часы", "2")

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Создать",
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
        from logic.teacher import create_lesson

        date = self.date_entry.get().strip()
        topic = self.topic_entry.get().strip()
        type_ = self.type_var.get()
        hours_str = self.hours_entry.get().strip()

        if not date or not topic:
            messagebox.showwarning("Ошибка", "Заполните дату и тему")
            return

        try:
            hours = int(hours_str) if hours_str else 2
        except ValueError:
            hours = 2

        if create_lesson(self.club["id"], date, topic, type_, hours):
            messagebox.showinfo("Успех", "Занятие создано")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать занятие")

# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВЛЕНИЕ ДОСТИЖЕНИЯ
# ============================================================

# ============================================================
# МОДАЛЬНОЕ ОКНО: ДОБАВЛЕНИЕ ДОСТИЖЕНИЯ
# ============================================================

class AddAchievementDialog(ctk.CTkToplevel):
    """Модалка добавления достижения студенту (с прокруткой)."""

    def __init__(self, parent, teacher_id, on_success):
        super().__init__(parent)

        self.teacher_id = teacher_id
        self.on_success = on_success

        self.title("Добавить достижение")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")
        self.transient(parent)

        # --- Внешний контейнер ---
        outer = ctk.CTkFrame(self, fg_color="#FFFFFF")
        outer.pack(fill="both", expand=True)

        # --- Заголовок (фиксированный, вне прокрутки) ---
        header = ctk.CTkFrame(outer, fg_color="#FFFFFF")
        header.pack(fill="x", padx=32, pady=(24, 8))

        ctk.CTkLabel(header, text="Добавить достижение",
                     font=("Inter", 18, "bold"),
                     text_color="#1E3A8A",
                     anchor="w").pack(fill="x")

        # --- ПРОКРУЧИВАЕМАЯ ОБЛАСТЬ С ФОРМОЙ ---
        scroll = ctk.CTkScrollableFrame(
            outer,
            fg_color="#FFFFFF",
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color="#94A3B8",
            corner_radius=0
        )
        scroll.pack(fill="both", expand=True, padx=(24, 12), pady=(0, 8))

        # Карточка внутри scroll
        card = ctk.CTkFrame(scroll, fg_color="#FFFFFF")
        card.pack(fill="both", expand=True, padx=8)

        # --- Студент ---
        ctk.CTkLabel(card, text="Студент",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        from logic.teacher import get_teacher_students
        students = get_teacher_students(teacher_id)

        if students:
            student_names = [
                f"{s['id']} — {s['fio']}" + (f" ({s['groups']})" if s.get("groups") else "")
                for s in students
            ]
            self.student_var = ctk.StringVar(value=student_names[0])
        else:
            student_names = ["Нет студентов"]
            self.student_var = ctk.StringVar(value="Нет студентов")

        ctk.CTkOptionMenu(
            card, values=student_names,
            variable=self.student_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # --- Название ---
        self.title_entry = self._add_field(card, "Название",
                                            "Олимпиада по программированию")

        # --- Тип ---
        ctk.CTkLabel(card, text="Тип",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.type_var = ctk.StringVar(value="Олимпиада")
        ctk.CTkOptionMenu(
            card, values=["Олимпиада", "Выставка", "Соревнование", "Конкурс"],
            variable=self.type_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # --- Уровень ---
        ctk.CTkLabel(card, text="Уровень",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.level_var = ctk.StringVar(value="Городской")
        ctk.CTkOptionMenu(
            card, values=["Городской", "Областной", "Региональный",
                          "Всероссийский", "Международный"],
            variable=self.level_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # --- Место ---
        ctk.CTkLabel(card, text="Место",
                     font=("Inter", 12, "bold"),
                     text_color="#334155",
                     anchor="w").pack(fill="x", pady=(0, 4))

        self.place_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(
            card, values=["1", "2", "3", "Участник"],
            variable=self.place_var,
            fg_color="#F8FAFC", button_color="#CBD5E1",
            text_color="#1E293B",
            font=("Inter", 13), height=40, corner_radius=8
        ).pack(fill="x", pady=(0, 14))

        # --- Дата ---
        self.date_entry = self._add_field(card, "Дата (ГГГГ-ММ-ДД)", "2026-10-25")

        # --- Результат ---
        self.result_entry = self._add_field(card, "Результат", "1 место")

        # --- Баллы ---
        self.points_entry = self._add_field(card, "Баллы", "10")

        # --- Отступ снизу, чтобы не прилипало ---
        ctk.CTkFrame(card, height=10, fg_color="transparent").pack(fill="x")

        # --- Кнопки (фиксированные, вне прокрутки) ---
        buttons = ctk.CTkFrame(outer, fg_color="#FFFFFF")
        buttons.pack(fill="x", padx=32, pady=(8, 24))

        ctk.CTkButton(
            buttons, text="Отмена",
            fg_color="transparent",
            border_width=1, border_color="#CBD5E1",
            text_color="#475569", hover_color="#F1F5F9",
            height=42, corner_radius=8,
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="Создать",
            fg_color="#2563EB", hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=42, corner_radius=8,
            command=self._on_save
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _add_field(self, parent, label, placeholder):
        """Поле с подписью."""
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
        """Создать достижение."""
        from logic.teacher import create_achievement

        student_str = self.student_var.get()
        try:
            student_id = int(student_str.split(" — ")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Ошибка", "Выберите студента")
            return

        title = self.title_entry.get().strip()
        type_ = self.type_var.get()
        level = self.level_var.get()
        place = self.place_var.get()
        date = self.date_entry.get().strip()
        result = self.result_entry.get().strip()
        points_str = self.points_entry.get().strip()

        if not title:
            messagebox.showwarning("Ошибка", "Введите название")
            return

        if not date:
            messagebox.showwarning("Ошибка", "Введите дату")
            return

        if not result:
            messagebox.showwarning("Ошибка", "Введите результат")
            return

        try:
            points = int(points_str) if points_str else 0
        except ValueError:
            points = 0

        if create_achievement(student_id, title, type_, level,
                              place, date, result, points):
            messagebox.showinfo("Успех", "Достижение добавлено")
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить")
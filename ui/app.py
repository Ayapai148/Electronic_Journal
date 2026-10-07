import customtkinter as ctk
from ui.theme import CONTENT_BG


class MainApp(ctk.CTk):
    """Единое окно приложения."""

    def __init__(self):
        super().__init__()

        #Настройки окна 
        self.title("ЭЖКСР - Электронный журнал")
        self.geometry("1440x1024")
        self.configure(fg_color=CONTENT_BG)

        # Текущий фрейм
        self.current_frame = None

        # Показать вход
        self.show_login()


    def _switch_frame(self, FrameClass, *args, **kwargs):
        """
        Переключить текущий фрейм.

        Args:
            FrameClass: класс фрейма
            *args, **kwargs: аргументы для конструктора
        """
        # Уничтожаем старый фрейм
        if self.current_frame is not None:
            self.current_frame.destroy()

        # Создаём новый
        self.current_frame = FrameClass(self, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        from ui.pages.login import LoginPage
        self._switch_frame(LoginPage,
                        on_success=self.on_login_success,
                        on_register=self.show_register)

    def show_register(self):
        """Показать страницу регистрации."""
        from ui.pages.register import RegisterPage
        self._switch_frame(RegisterPage, on_success=self.show_login,
                           on_cancel=self.show_login)

    def on_login_success(self, user):
        """
        Обработка успешного входа.

        Args:
            user: словарь с данными пользователя
        """
        role = user.get("role", "")

        if role == "teacher":
            self.show_teacher(user)
        elif role == "admin":
            self.show_admin(user)
        elif role == "student":
            self.show_student(user)


    def show_teacher(self, user):
        """Показать панель преподавателя."""
        from ui.pages.teacher import TeacherApp
        self._switch_frame(TeacherApp, user=user, on_logout=self.show_login)

    def show_student(self, user):
        """Показать панель студента."""
        from ui.pages.student import StudentApp
        self._switch_frame(StudentApp, user=user, on_logout=self.show_login)

    def show_admin(self, user):
        """Показать панель администратора."""
        from ui.pages.admin import AdminApp
        self._switch_frame(AdminApp, user=user, on_logout=self.show_login)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
from db.database import init_db
from ui.login import LoginWindow


def main():
    init_db()
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
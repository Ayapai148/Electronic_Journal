from db.database import init_db
from ui.app import MainApp


def main():
    init_db()
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
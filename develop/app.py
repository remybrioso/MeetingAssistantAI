from application.app_controller import AppController
from gui.main_window import MainWindow


def main():

    controller = AppController()

    app = MainWindow(controller)

    app.mainloop()


if __name__ == "__main__":
    main()
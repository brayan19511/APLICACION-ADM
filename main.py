import sys
from PySide6.QtWidgets import QApplication
from controllers.main_controller import MainController


if __name__=='__main__':
    app =QApplication(sys.argv)
    main=MainController()

    main.run()

    sys.exit(app.exec())


 
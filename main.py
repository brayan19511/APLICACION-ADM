import sys
from PySide6.QtWidgets import QApplication
from modules.main.presenter import MainPresenter

if __name__=='__main__':
    app =QApplication(sys.argv)
    # main=MainController()
    main=MainPresenter()
    main.run()

    sys.exit(app.exec())


 
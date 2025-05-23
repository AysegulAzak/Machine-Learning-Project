from PySide6.QtCore import QObject, Signal

class signals(QObject):
    style1_signal = Signal()  # Sağ kol
    style2_signal = Signal()  # Sol kol
    style3_signal = Signal()  # Lateral raise

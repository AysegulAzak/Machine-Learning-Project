import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from videoWorker import VideoWorker
from signals import signals

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dambıl Takip Sistemi")
        self.setGeometry(100, 100, 300, 200)

        self.style1_count = 0
        self.style2_count = 0
        self.style3_count = 0

        self.label1 = QLabel("Sağ Kol Sayısı: 0")
        self.label2 = QLabel("Sol Kol Sayısı: 0")
        self.label3 = QLabel("Lateral Raise Sayısı: 0")

        for label in (self.label1, self.label2, self.label3):
            label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.addWidget(self.label3)
        self.setLayout(layout)

        self.worker = VideoWorker()

        # Sinyalleri bağlama
        self.worker.style1_detected.connect(self.update_style1)
        self.worker.style2_detected.connect(self.update_style2)
        self.worker.style3_detected.connect(self.update_style3)

        self.worker.start()

    def update_style1(self):
        self.style1_count += 1
        self.label1.setText(f"Sağ Kol Sayısı: {self.style1_count}")

    def update_style2(self):
        self.style2_count += 1
        self.label2.setText(f"Sol Kol Sayısı: {self.style2_count}")

    def update_style3(self):
        self.style3_count += 1
        self.label3.setText(f"Lateral Raise Sayısı: {self.style3_count}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

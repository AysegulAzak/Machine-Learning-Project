from PySide6.QtCore import QThread, Signal
import cv2
from dumble import DumbleCounter
import time

class VideoWorker(QThread):
    style1_detected = Signal()  # Sağ kol sinyali
    style2_detected = Signal()  # Sol kol sinyali
    style3_detected = Signal()  # Lateral raise sinyali

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

        # Kamera çözünürlüğünü ayarla
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.dumble_counter = DumbleCounter()

        # Kol hareket bayrakları
        self.right_arm_up = False
        self.left_arm_up = False
        self.lateral_raised = False

        # Debounce için zaman
        self.last_right_time = 0
        self.last_left_time = 0
        self.last_lateral_time = 0

        # Başlangıç durumu sayım yapmaması için
        self.lateral_initialized = False
        self.right_initialized = False
        self.left_initialized = False

    def run(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = self.dumble_counter.process_frame(frame)
            style_left, style_right, style_lateral = self.detect_styles(frame)

            current_time = time.time()

            # Sağ kol
            if not self.right_initialized:
                if style_right == "Up":
                    self.right_arm_up = True
                self.right_initialized = True
            else:
                if style_right == "Up" and not self.right_arm_up:
                    self.right_arm_up = True
                elif style_right == "Down" and self.right_arm_up:
                    if current_time - self.last_right_time > 1:
                        self.right_arm_up = False
                        self.last_right_time = current_time
                        self.style1_detected.emit()
                        print("Sağ tekrar sayıldı.")

            # Sol kol
            if not self.left_initialized:
                if style_left == "Up":
                    self.left_arm_up = True
                self.left_initialized = True
            else:
                if style_left == "Up" and not self.left_arm_up:
                    self.left_arm_up = True
                elif style_left == "Down" and self.left_arm_up:
                    if current_time - self.last_left_time > 1:
                        self.left_arm_up = False
                        self.last_left_time = current_time
                        self.style2_detected.emit()
                        print("Sol tekrar sayıldı.")

            # Lateral raise
            if not self.lateral_initialized:
                if style_lateral == "Raised":
                    self.lateral_raised = True
                self.lateral_initialized = True
            else:
                if style_lateral == "Raised" and not self.lateral_raised:
                    if current_time - self.last_lateral_time > 1:
                        self.lateral_raised = True
                        self.last_lateral_time = current_time
                        self.style3_detected.emit()
                        print("Lateral tekrar sayıldı.")
                elif style_lateral == "Lowered" and self.lateral_raised:
                    self.lateral_raised = False

            cv2.imshow("Dumble Counter", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def detect_styles(self, frame):
        style_left = None
        style_right = None
        style_lateral = None
        landmarks = self.dumble_counter.get_landmarks(frame)

        if landmarks:
            try:
                mp_pose = self.dumble_counter.mp_pose

                # Sağ kol
                shoulder_r = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                elbow_r = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
                wrist_r = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                angle_r = self.dumble_counter.calculate_angle(shoulder_r, elbow_r, wrist_r)

                if angle_r > 160:
                    style_right = "Down"
                elif angle_r < 60:
                    style_right = "Up"

                # Sol kol
                shoulder_l = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                elbow_l = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                wrist_l = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                angle_l = self.dumble_counter.calculate_angle(shoulder_l, elbow_l, wrist_l)

                if angle_l > 160:
                    style_left = "Down"
                elif angle_l < 60:
                    style_left = "Up"

                # Lateral Raise kontrolü
                hip_r = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                hip_l = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

                angle_r_lat = self.dumble_counter.calculate_angle(shoulder_r, hip_r, wrist_r)
                angle_l_lat = self.dumble_counter.calculate_angle(shoulder_l, hip_l, wrist_l)

                if angle_r_lat < 90 and angle_l_lat < 90:
                    style_lateral = "Raised"
                else:
                    style_lateral = "Lowered"

            except Exception as e:
                print("Açı hesaplama hatası:", e)

        return style_left, style_right, style_lateral

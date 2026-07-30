import cv2
import mediapipe as mp
import csv
import os

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5,
)

DATA_FILE = "data/gesture_data.csv"
os.makedirs("data", exist_ok=True)

# Create CSV with header if it doesn't exist yet
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        header = []
        for i in range(21):
            header += [f"x{i}", f"y{i}", f"z{i}"]
        header.append("label")
        writer.writerow(header)

cap = cv2.VideoCapture(0)

print("Instructions:")
print("  Hold the SIGNAL FOR HELP gesture, then press 's' to save as SIGNAL (1)")
print("  Do a NORMAL hand movement, then press 'n' to save as NORMAL (0)")
print("  Press 'q' to quit")

count_signal = 0
count_normal = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    landmarks_row = None
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks_row = []
            for lm in hand_landmarks.landmark:
                landmarks_row += [lm.x, lm.y, lm.z]

    cv2.putText(frame, f"Signal: {count_signal}  Normal: {count_normal}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "s=signal  n=normal  q=quit",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Data Collection", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') and landmarks_row:
        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(landmarks_row + [1])
        count_signal += 1
        print(f"Saved SIGNAL sample #{count_signal}")

    elif key == ord('n') and landmarks_row:
        with open(DATA_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(landmarks_row + [0])
        count_normal += 1
        print(f"Saved NORMAL sample #{count_normal}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Done. Total signal: {count_signal}, Total normal: {count_normal}")
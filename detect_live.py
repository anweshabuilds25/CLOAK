import cv2
import mediapipe as mp
import time
from classifier import predict

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

HOLD_TIME_REQUIRED = 1.5  # seconds
signal_start_time = None
triggered = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    label_text = "No hand detected"
    color = (200, 200, 200)

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        landmarks = []
        for lm in hand_landmarks.landmark:
            landmarks.extend([lm.x, lm.y, lm.z])

        pred = predict(landmarks)

        if pred == 1:
            if signal_start_time is None:
                signal_start_time = time.time()
            elapsed = time.time() - signal_start_time

            if elapsed >= HOLD_TIME_REQUIRED:
                label_text = "ALERT TRIGGERED!"
                color = (0, 0, 255)
                triggered = True
            else:
                label_text = f"Signal detected... holding ({elapsed:.1f}s)"
                color = (0, 165, 255)
        else:
            signal_start_time = None
            triggered = False
            label_text = "Normal"
            color = (0, 255, 0)
    else:
        signal_start_time = None
        triggered = False

    cv2.putText(frame, label_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                1, color, 2)
    cv2.imshow("CLOAK - Live Detection Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
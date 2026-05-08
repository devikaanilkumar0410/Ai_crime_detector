# import os
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()

# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# def run_detection(video_path):
#     import cv2
#     from ultralytics import YOLO
#     import mediapipe as mp
    

#     # Init models
#     yolo_model = YOLO("yolov8n.pt")

#     mp_pose = mp.solutions.pose
#     pose = mp_pose.Pose()
#     mp_draw = mp.solutions.drawing_utils

#     cap = cv2.VideoCapture(video_path)

#     prev_hand_y = None
#     aggressive_threshold = 20

#     alert_triggered = False

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         person_detected = False

#         frame = cv2.resize(frame, (640, 480))

#         alert_text = ""
#         ai_text = ""

#         # ------------------- MEDIAPIPE -------------------
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results_pose = pose.process(rgb_frame)

#         aggressive_detected = False

#         if results_pose.pose_landmarks:
#             mp_draw.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#             landmarks = results_pose.pose_landmarks.landmark

#             lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
#             rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
#             ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
#             rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

#             lw_y = lw.y * frame.shape[0]
#             rw_y = rw.y * frame.shape[0]
#             ls_y = ls.y * frame.shape[0]
#             rs_y = rs.y * frame.shape[0]

#             # Hands raised
#             if lw_y < ls_y or rw_y < rs_y:
#                 aggressive_detected = True

#             # Sudden movement
#             if prev_hand_y is not None:
#                 movement = abs(lw_y - prev_hand_y)
#                 if movement > aggressive_threshold:
#                     aggressive_detected = True

#             prev_hand_y = lw_y

#         # ------------------- YOLO -------------------
#         results = yolo_model(frame, conf=0.7)

#         for r in results:
#             for box in r.boxes:
#                 cls = int(box.cls[0])

#                 if cls == 0:
#                     person_detected = True
#                     x1, y1, x2, y2 = map(int, box.xyxy[0])
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     cv2.putText(frame, "Person", (x1, y1 - 10),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         # ------------------- ALERT -------------------
#         if aggressive_detected and person_detected and not alert_triggered:
#             alert_text = "🚨 Suspicious Activity Detected"
#             from PIL import Image
#             import google.generativeai as genai

#             # Convert frame to image
#             img = Image.fromarray(frame)

#             # Call GenAI
#             response = genai.GenerativeModel('gemini-2.5-flash').generate_content(
#                 ["This is a CCTV image. Describe clearly what suspicious activity is happening.", img]
#             )

#             ai_text = response.text

            

#             alert_triggered = True
#         else:
#             alert_text = "✅ No Suspicious Activity Detected"

            

#         # ------------------- RETURN -------------------
#         yield frame, alert_text, ai_text

#     cap.release()






import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def run_detection(video_path):
    import cv2
    from ultralytics import YOLO
    import mediapipe as mp
    from PIL import Image

    # ---------------- INIT ----------------
    yolo_model = YOLO("yolov8n.pt")

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(video_path)

    prev_hand_y = None
    aggressive_threshold = 20

    # ✅ NEW: LOCK SYSTEM
    suspicious_lock = False
    ai_called = False   # to avoid repeated API calls

    # ---------------- LOOP ----------------
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        person_detected = False
        frame = cv2.resize(frame, (640, 480))

        alert_text = ""
        ai_text = ""

        # ---------------- MEDIAPIPE ----------------
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_pose = pose.process(rgb_frame)

        aggressive_detected = False

        if results_pose.pose_landmarks:
            mp_draw.draw_landmarks(frame, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            landmarks = results_pose.pose_landmarks.landmark

            lw = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
            rw = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            lw_y = lw.y * frame.shape[0]
            rw_y = rw.y * frame.shape[0]
            ls_y = ls.y * frame.shape[0]
            rs_y = rs.y * frame.shape[0]

            # 🔹 Hands raised
            if lw_y < ls_y or rw_y < rs_y:
                aggressive_detected = True

            # 🔹 Sudden movement
            if prev_hand_y is not None:
                movement = abs(lw_y - prev_hand_y)
                if movement > aggressive_threshold:
                    aggressive_detected = True

            prev_hand_y = lw_y

        # ---------------- YOLO ----------------
        results = yolo_model(frame, conf=0.7)

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])

                if cls == 0:  # person
                    person_detected = True
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Person", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # ---------------- ALERT LOGIC ----------------
        if aggressive_detected and person_detected:
            suspicious_lock = True  # 🔒 lock once triggered
            alert_text = "🚨 Suspicious Activity Detected"

            # 🧠 Call AI ONLY ONCE
            if not ai_called:
                img = Image.fromarray(frame)

                response = genai.GenerativeModel('gemini-2.5-flash').generate_content(
                    ["This is a CCTV image. Describe clearly what suspicious activity is happening.", img]
                )

                ai_text = response.text
                ai_called = True

        elif suspicious_lock:
            # 🔒 Keep showing suspicious
            alert_text = "🚨 Suspicious Activity Detected"

        else:
            alert_text = "✅ No Suspicious Activity Detected"

        # ---------------- RETURN ----------------
        yield frame, alert_text, ai_text

    cap.release()
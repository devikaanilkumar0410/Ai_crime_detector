# import streamlit as st
# import tempfile
# from detect_sus import run_detection
# import cv2

# st.title("AI Surveillance System 🚨")

# # ---------------- SESSION STATE ----------------
# if "run" not in st.session_state:
#     st.session_state.run = False

# if "alert_shown" not in st.session_state:
#     st.session_state.alert_shown = False


# # ---------------- UPLOAD ----------------
# uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

# # ---------------- BUTTONS ----------------
# col1, col2 = st.columns(2)

# with col1:
#     if st.button("▶️ Play"):
#         st.session_state.run = True
#         st.session_state.alert_shown = False   # reset alert

# with col2:
#     if st.button("⏹️ Stop"):
#         st.session_state.run = False


# # ---------------- VIDEO PROCESS ----------------
# if uploaded_file is not None:
#     tfile = tempfile.NamedTemporaryFile(delete=False)
#     tfile.write(uploaded_file.read())

#     stframe = st.empty()

#     if st.session_state.run:
#         for frame, alert_text, ai_text in run_detection(tfile.name):

#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             stframe.image(frame)

#             # 🚨 ALERT (only once)
#             # if alert_text and not st.session_state.alert_shown:
#             #     st.error(alert_text)

#             #     st.session_state.alert_shown = True
#             # 🚨 Suspicious
#             if "🚨" in alert_text and not st.session_state.alert_shown:
#                 st.error(alert_text)
#                 st.session_state.alert_shown = True

#             # ✅ Normal
#             elif "✅" in alert_text:
#                 st.success(alert_text)

#             # 🧠 AI text
#             if ai_text:
#                 st.write("AI:", ai_text)

#             # ⏸️ Stop loop if paused
#             if not st.session_state.run:
#                 break





import streamlit as st
import tempfile
from detect_sus import run_detection
import cv2

st.title("AI Surveillance System 🚨")

# ---------------- SESSION STATE ----------------
if "run" not in st.session_state:
    st.session_state.run = False

if "alert_shown" not in st.session_state:
    st.session_state.alert_shown = False

# ✅ NEW: track last status
if "last_status" not in st.session_state:
    st.session_state.last_status = ""


# ---------------- UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Video", type=["mp4"])

# ---------------- BUTTONS ----------------
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Play"):
        st.session_state.run = True
        st.session_state.alert_shown = False
        st.session_state.last_status = ""   # ✅ reset status

with col2:
    if st.button("⏹️ Stop"):
        st.session_state.run = False


# ---------------- VIDEO PROCESS ----------------
if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    stframe = st.empty()
    status_box = st.empty()   # ✅ NEW: placeholder for messages

    if st.session_state.run:
        for frame, alert_text, ai_text in run_detection(tfile.name):

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            stframe.image(frame)

            # ✅ SHOW STATUS ONLY WHEN IT CHANGES
            if alert_text and alert_text != st.session_state.last_status:

                if "🚨" in alert_text:
                    status_box.error(alert_text)

                else:
                    status_box.success(alert_text)


                st.session_state.last_status = alert_text

            # 🧠 AI text
            if ai_text:
                st.write("AI:", ai_text)

            # ⏸️ Stop loop if paused
            if not st.session_state.run:
                break
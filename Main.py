from tkinter import *
from PIL import Image, ImageTk
import cv2
from tkinter import filedialog
import mediapipe as mp
import pyttsx3

root = Tk()
width = root.winfo_screenwidth()
height = root.winfo_screenheight()
root.geometry("%dx%d" % (width, height))
root.configure(bg="#f0f0f5")
root.title('Sign Language App')

# Images
flag = PhotoImage(file="egypt_flag.png").subsample(12)
govern = PhotoImage(file="govern logo.png").subsample(3)

Label(root, image=flag).place(x=50, y=50)
Label(root, image=govern).place(x=width - 250, y=30)

Label(root, text='SignSpeak app', font=('Helvetica', 25, 'bold'), bd=5, bg='#2C3E50', fg='#FFFFFF', relief=SOLID, width=200).pack(pady=50, padx=300)

# Variables
finger_tips = [8, 12, 16, 20]
thumb_tip = 4
w = 500
h = 400
engine = pyttsx3.init()
cap = cv2.VideoCapture(0)
speech_enabled = BooleanVar(value=True)  # speech is ON by default

label1 = Label(root, width=w, height=h, bg="#ECF0F1")
label1.place(x=250, y=200)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

running = False
last_message = ""

# Detect hand sign
def detect_sign(lm_list):
    if lm_list[8].y < lm_list[7].y and lm_list[12].y < lm_list[11].y:
        if lm_list[16].y > lm_list[15].y and lm_list[20].y > lm_list[19].y:
            return "Yes, we won."

    if lm_list[8].y < lm_list[7].y and lm_list[20].y < lm_list[19].y:
        if lm_list[12].y > lm_list[11].y and lm_list[16].y > lm_list[15].y:
            if lm_list[4].x < lm_list[3].x:
                return "I love you!"

    if lm_list[4].y < lm_list[3].y:
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y and lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return "Like!"

    if lm_list[4].y > lm_list[3].y:
        if lm_list[8].y > lm_list[6].y and lm_list[12].y > lm_list[10].y and lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
            return "Dislike"

    if lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
        if lm_list[4].x < lm_list[3].x:
            return "Stop!"

    if abs(lm_list[4].x - lm_list[8].x) < 0.03 and abs(lm_list[4].y - lm_list[8].y) < 0.03:
        if lm_list[12].y < lm_list[10].y and lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y:
            return "Perfect!"

    if lm_list[4].y < lm_list[3].y and lm_list[8].y < lm_list[7].y and lm_list[12].y < lm_list[11].y and lm_list[16].y < lm_list[15].y and lm_list[20].y < lm_list[19].y:
        return "Me or My self!"

    return "no sign detected"

# Speak
def speak_message(message):
    engine.say(message)
    engine.runAndWait()

# Start live
def start_live():
    global running
    running = True
    live()

# Stop live
def stop_live():
    global running
    running = False
    label1.config(image='')  # Hide camera
    status.config(text="Camera stopped")

# Live camera
def live():
    global img, last_message
    if not running:
        return

    _, img = cap.read()
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    message = ""

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = [lm for lm in hand.landmark]
            message = detect_sign(lm_list)
            mpDraw.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)

    image = Image.fromarray(rgb)
    finalImage = ImageTk.PhotoImage(image)
    label1.configure(image=finalImage)
    label1.image = finalImage
    status.configure(text=message)


    if message != "no sign detected" and message != last_message:
        speak_message(message)
        last_message = message
    elif message == "no sign detected":
        last_message = ""

    root.after(50, live)

# Open and process video
def video():
    global last_message
    path = filedialog.askopenfilename()
    if not path:
        return

    video_cap = cv2.VideoCapture(path)
    while video_cap.isOpened():
        ret, frame = video_cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (w, h))
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)
        message = ""

        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                lm_list = [lm for lm in hand.landmark]
                message = detect_sign(lm_list)
                mpDraw.draw_landmarks(frame, hand, mpHands.HAND_CONNECTIONS)

        image = Image.fromarray(rgb)
        finalImage = ImageTk.PhotoImage(image)
        label1.configure(image=finalImage)
        label1.image = finalImage
        status.configure(text=message)

        if message != "no sign detected" and message != last_message:
            speak_message(message)
            last_message = message
        elif message == "no sign detected":
            last_message = ""

        root.update()
        cv2.waitKey(50)

    video_cap.release()
    label1.config(image='')
    status.config(text="Video finished")

# About
def about():
    about_win = Toplevel()
    about_win.title("About the developer")
    about_win.geometry("300x100")

    Label(about_win, text="Name: Hossam Fekry", font=('Helvetica', 12, 'bold')).pack()
    Label(about_win, text="Prim: 6", font=('Helvetica', 12, 'bold')).pack()
    Label(about_win, text="School: Modern Age schools (MAS)", font=('Helvetica', 12, 'bold')).pack()

def speak_message(message):
    if speech_enabled.get():
        engine.say(message)
        engine.runAndWait()


# Status label
status = Label(root, text="", font=('Helvetica', 18, 'bold'), bd=5, bg='gray', width=50, fg='#FFFFFF', relief=GROOVE)
status.place(x=400, y=650)

# Buttons
Button(root, text='Live', padx=95, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=start_live).place(x=width - 250, y=450)
Button(root, text='Video', padx=95, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=video).place(x=width - 250, y=500)
Button(root, text='Stop', padx=95, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=stop_live).place(x=width - 250, y=550)
Button(root, text='About', padx=95, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=about).place(x=width - 250, y=600)
Button(root, text='Exit', padx=95, bg='#2C3E50', fg='white', relief=FLAT, font=('Helvetica', 12, 'bold'), command=lambda: root.destroy()).place(x=650, y=700)
Checkbutton(root, text="Enable Speech", variable=speech_enabled, bg="#f0f0f5", font=('Helvetica', 12)).place(x=width - 250, y=400)


# School logo
school_logo = PhotoImage(file="school logo.png")
Label(root, image=school_logo).place(x=width - 700, y=300)

root.mainloop()

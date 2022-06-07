# python main.py --shape-predictor eye_predictor.dat
import tkinter
from tkinter import *
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2
import tkinter as tk
from threading import Thread
import pyttsx3

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

dict = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
        '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
        '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
        '...-': 'v', '.--': 'w', '-..-': 'x', '-.---': 'y', '--..': 'z', '-----': "0",
        '.----': "1", '..---': "2", '...--': "3", '....-': "4", '.....': "5", '-....': "6", '--...': "7",
        '---..': "8", '----.': "9", '.-.-.': '+', '.--.-.': '@'}


def eye_aspect_ratio(eye):

    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    return ear


# parses the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
                help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="",
                help="path to input video file")
args = vars(ap.parse_args())


def func():
    stopBtn = tk.Button(root, text='Stop', width=25, command=stopDetection)
    stopBtn.pack()


def slider1(val):
    return(sli1.get())


def slider2(val):
    return(sli2.get())


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def startdetection():
    EYE_AR_THRESH = slider1(0)

    EYE_AR_CONSEC_FRAMES = slider2(0)

    COUNTER = 0
    TOTAL = 0
    begin = 0
    end = 0
    i = 0

    symVar.set("Current Symbol:")
    letterVar.set("Symbol to Letter:")
    wordVar.set("Current Word:")
    print("Loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # 43,48
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]  # 37,42
    print(lStart, lEnd, rStart, rEnd)
    # start the video
    print("Starting video stream ...")
    vs = VideoStream(src=0).start()

    # loop over frames from the video stream
    blinkop = []
    printword = []
    sent = []

    while True:
        # symVar.set("Current Symbol: "+" ".join(blinkop))

        currSym = "".join(blinkop)
        if dict.get(currSym) != None:
            letterVar.set("Symbol to Letter: "+dict[currSym])
        else:
            letterVar.set("Symbol to Letter: ")

        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = detector(gray, 0)
        # looping the face detections
        for rect in rects:

            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[6:13]
            rightEye = shape[0:6]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                COUNTER += 1
                begin = time.time()

            else:
                end = time.time()

                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    TOTAL += 1

                    if elapse > 0 and elapse <= 1:
                        i = i+1
                        print(i, ".")
                        blinkop.append('.')
                        # winsound.Beep(500, 100)
                    elif elapse > 1 and elapse <= 3:
                        i = i+1
                        print(i, "-")
                        blinkop.append('-')
                        # winsound.Beep(500,100)
                    key = cv2.waitKey(1) & 0xFF

                    symVar.set("Current Symbol: "+" ".join(blinkop))

                COUNTER = 0

            elapse = begin-end

            # cv2.putText(frame, "th: {}".format(EYE_AR_CONSEC_FRAMES),
            #             (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "EAR: {:.2f}".format(
                ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # height, width, no_channels = frame.shape
        # canvas = tkinter.Canvas(root, width=width, height=height)
        # canvas.pack()

        # print("jhgkldfhgdfgjj")
        # photo = ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
        # canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
        # time.sleep(1000)
        # show the frame
        cv2.imshow("Morse Code detection with Eye Blinks", frame)
        key = cv2.waitKey(1) & 0xFF

        condition(key, blinkop, printword, sent)

        if key == ord("q"):
            break

        if stop == 1:
            break
    cv2.destroyAllWindows()
    vs.stop()


def condition(key, blinkop, printword, sent):

    if key == ord("w"):
        # print(blinkop)
        # list to string
        cmpp = 0
        cmpp = ''.join([str(elem) for elem in blinkop])
        # print(cmpp)
        if dict.get(cmpp) != None:
            tempword = dict[cmpp]  # temp varibale to make word
            print(dict[cmpp])
            print("letter is printed")
            printword.append(tempword)  # adding letters of word in list

            blinkop.clear()
            symVar.set("Current Symbol:")
            wordVar.set("Current Word: "+"".join(printword))

    if key == ord("n"):
        actual_word = ''.join([str(elem) for elem in printword])
        sent.append(actual_word)
        printword.clear()
        wordVar.set("Current Word: "+"".join(printword))
        sentVar.set("Current Sentence: "+" ".join(sent))

    if key == ord("s"):
        sentence = ' '.join([str(elem) for elem in sent])
        speak(sentence)

        wordVar.set("Current Word: "+"".join(""))

    if key == ord("\b"):
        # if 'back' in query:
        if len(blinkop):
            blinkop.pop(-1)
            symVar.set("Current Symbol: "+" ".join(blinkop))


def startDetection():
    global stop
    stop = 0

    t = Thread(target=startdetection)
    #t2 = Thread(target=takeCommand)
    t.start()
    # t2.start()


def stopDetection():
    global stop
    stop = 1


font = ("Calibri", 20, "bold")

root = tkinter.Tk()
root.geometry("500x500")
root.title('Blink Detection Using Morse Code')
root["bg"] = "#4b4bfa"

sli1 = Scale(root, from_=0, to=0.5, resolution=0.01, orient=HORIZONTAL, fg="red", bg="yellow", command=slider1, label="EAR THRESHOULD VALUE", length=150,
             highlightbackground="red", highlightcolor="black")
sli1.pack(pady=10)
sli1.place(x=90, y=30)

sli2 = Scale(root, from_=1, to=30, resolution=2, orient=HORIZONTAL, fg="red", bg="yellow", command=slider2, label="FRAME", length=150,
             highlightbackground="red", highlightcolor="black")
sli2.pack(pady=10)
sli2.place(x=270, y=30)

button = tk.Button(root, text='Start', width=10,
                   command=startDetection, font=font, bg="white")
button.pack(pady=10)
button.place(x=90, y=120)

stopBtn = tk.Button(root, text='Stop', width=10,
                    command=stopDetection, font=font, bg="white")
stopBtn.pack(pady=10)
stopBtn.place(x=270, y=120)


symVar = tk.StringVar()
symVar.set("Current Symbol: ")
symLabel = tk.Label(root, textvariable=symVar,
                    font=font, bg="#4b4bfa", fg="white")
symLabel.pack(pady=10)
symLabel.place(x=90, y=210)


letterVar = tk.StringVar()
letterVar.set("Symbol to Letter: ")
letterLabel = tk.Label(root, textvariable=letterVar,
                       font=font, bg="#4b4bfa", fg="white")
letterLabel.pack(pady=10)
letterLabel.place(x=90, y=270)

wordVar = tk.StringVar()
wordVar.set("Current Word: ")
wordLabel = tk.Label(root, textvariable=wordVar,
                     font=font, bg="#4b4bfa", fg="white")
wordLabel.pack(pady=10)
wordLabel.place(x=90, y=330)

sentVar = tk.StringVar()
sentVar.set("Current Sentence: ")
sentLabel = tk.Label(root, textvariable=sentVar,
                     font=font, bg="#4b4bfa", fg="white")
sentLabel.pack(pady=10)
sentLabel.place(x=90, y=390)

root.mainloop()

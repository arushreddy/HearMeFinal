import cv2
import mediapipe as mp
import csv
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

letter = input("Enter Letter (or) Sentence: ").upper()

filename = "asl_data.csv"

while True:

    ret,frame=cap.read()

    frame=cv2.flip(frame,1)

    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    result=hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand in result.multi_hand_landmarks:

            data=[]

            for lm in hand.landmark:

                data.append(lm.x)
                data.append(lm.y)
                data.append(lm.z)

            # Only save correct rows
            if len(data)==63:

                with open(filename,'a',newline='') as f:

                    writer=csv.writer(f)

                    writer.writerow([letter]+data)

    cv2.imshow("Collect Data",frame)

    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()
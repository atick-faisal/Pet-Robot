import cv2 as cv
import numpy as np
import RPi.GPIO as GPIO
import time

#GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 50)
p.start(2.5)
p.ChangeDutyCycle(6.25)
time.sleep(1)

currentPosition = 6.25
font = cv.FONT_HERSHEY_SIMPLEX

lower = (10, 170, 100)
upper = (20, 255, 255)

cap = cv.VideoCapture(0)
ret, frame = cap.read()

# frame = cv.imread('test.jpg')
# frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
# roi = cv.selectROI(frame, False)
# x = roi[0]
# y = roi[1]
# w = roi[2]
# h = roi[3]
# frame = frame[x:x+w, y:y+h]
#
# print(frame)
#
# hm = frame[:,:,0].mean()
# sm = frame[:,:,1].mean()
# vm = frame[:,:,2].mean()
#
# print(hm)
# hue_l = hm - 10;
# hue_h = hm + 10;
#
# sat_l = sm - 50;
# sat_h = sm + 50;
#
# val_l = vm - 50;
# val_h = vm + 50;
#
# lower = (hue_l, 170, 100)
# upper = (hue_h, 255, 255)
# print(frame[:,:,0].mean(), frame[:,:,1].mean(), frame[:,:,2].mean())

lower = (10, 170, 100)
upper = (20, 255, 255)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv, lower, upper)
    cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv.contourArea)
        ((x, y), radius) = cv.minEnclosingCircle(c)
        M = cv.moments(c)
        if M["m00"] != 0:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            cv.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv.circle(frame, center, 5, (0, 0, 255), -1)
            dist = (0.25*140) / (radius*2)
            dx = (x + radius) - 320
            s = abs(dx)*0.001648*dist
            theta = (180 * np.arctan(s/dist)) / 3.14
            theta = float("{0:.2f}".format(theta))

            if dx > 0 and theta > 15 and currentPosition > 2.25:
                p.ChangeDutyCycle(currentPosition - 0.25)
                time.sleep(0.01)
                #cv.putText(frame, "Angle : " + str(theta) + "deg left", center, font, 0.5, (255,255,255), 2)
            elif dx < 0 and theta > 15 and currentPosition < 11:
                p.ChangeDutyCycle(currentPosition + 0.25)
                time.sleep(0.01)
                #cv.putText(frame, "Angle : " + str(theta) + "deg right", center, font, 0.5, (255,255,255), 2)

            dist = float("{0:.2f}".format(dist))
            cv.putText(frame, "Distance : " + str(dist) + "m", (center[0], center[1] - 20), font, 0.5, (255,255,255), 2)

    cv.imshow("Frame", frame)

    k = cv.waitKey(30) & 0xFF
    if k == 27:
        break

cap.release()
cv.destroyAllWindows()

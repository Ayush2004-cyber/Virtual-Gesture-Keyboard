
import cv2
import numpy as np
from pynput.keyboard import Key, Controller
import time

keyboard = Controller()


LOWER_DARK_BLUE = np.array([100, 100, 20]) 
UPPER_DARK_BLUE = np.array([130, 255, 100]) 

LOWER_BLACK = np.array([0, 0, 0])
UPPER_BLACK = np.array([180, 255, 30]) 


MIN_CONTOUR_AREA = 500  
DETECTION_STABILITY_FRAMES = 15 
PRESS_COOLDOWN_SECONDS = 0.5 

dark_blue_detection_count = 0
black_detection_count = 0
last_press_time = {'space': 0, 'backspace': 0}

def open_mobile_camera_and_detect_colors():
    global dark_blue_detection_count
    global black_detection_count
    global last_press_time

    """
    Opens mobile camera stream, detects specified objects by color,
    and simulates key presses.
    """
    mobile_camera_url = "http://100.69.107.72:8080/video" 
    cap = cv2.VideoCapture(mobile_camera_url)

    if not cap.isOpened():
        print(f"Error: Could not open mobile camera stream from {mobile_camera_url}.")
        print("Please ensure:")
        print("1. Your phone and computer are on the SAME Wi-Fi network.")
        print("2. The IP Webcam app is running on your phone and the server is started.")
        print("3. The IP address and port are correct and active.")
        return

    print(f"Mobile camera feed opened from {mobile_camera_url}.")
    print("Hold Object A (DARK BLUE) to press SPACE.")
    print("Hold Object B (BLACK) to press BACKSPACE.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame from mobile camera. Exiting...")
            break

        blurred_frame = cv2.GaussianBlur(frame, (7, 7), 0)

        hsv_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

        mask_dark_blue = cv2.inRange(hsv_frame, LOWER_DARK_BLUE, UPPER_DARK_BLUE)
        mask_dark_blue = cv2.erode(mask_dark_blue, None, iterations=2) 
        mask_dark_blue = cv2.dilate(mask_dark_blue, None, iterations=2)

        contours_dark_blue, _ = cv2.findContours(mask_dark_blue.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_dark_blue = False
        for contour in contours_dark_blue:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA:
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                if radius > 10: 
                    cv2.circle(frame, (int(x), int(y)), int(radius), (130, 0, 0), 2)
                    cv2.putText(frame, "Object A (SPACE)", (int(x) - 50, int(y) - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (130, 0, 0), 2)
                    detected_dark_blue = True
                    break 

        if detected_dark_blue:
            dark_blue_detection_count += 1
            if dark_blue_detection_count >= DETECTION_STABILITY_FRAMES:
                current_time = time.time()
                if (current_time - last_press_time['space']) > PRESS_COOLDOWN_SECONDS:
                    print("Object A (DARK BLUE) detected stable -> Pressing SPACE")
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                    last_press_time['space'] = current_time
        else:
            dark_blue_detection_count = 0

        mask_black = cv2.inRange(hsv_frame, LOWER_BLACK, UPPER_BLACK)
        mask_black = cv2.erode(mask_black, None, iterations=2) 
        mask_black = cv2.dilate(mask_black, None, iterations=2)

        contours_black, _ = cv2.findContours(mask_black.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_black = False
        for contour in contours_black:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA:
                ((x, y), radius) = cv2.minEnclosingCircle(contour)
                if radius > 10: 
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 0, 0), 2)
                    cv2.putText(frame, "Object B (BACKSPACE)", (int(x) - 70, int(y) - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                    detected_black = True
                    break

        if detected_black:
            black_detection_count += 1
            if black_detection_count >= DETECTION_STABILITY_FRAMES:
                current_time = time.time()
                if (current_time - last_press_time['backspace']) > PRESS_COOLDOWN_SECONDS:
                    print("Object B (BLACK) detected stable -> Pressing BACKSPACE")
                    keyboard.press(Key.backspace)
                    keyboard.release(Key.backspace)
                    last_press_time['backspace'] = current_time
        else:
            black_detection_count = 0

        # Display the final frame
        cv2.imshow('Virtual Keyboard - Color Detection - Press Q to Quit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    open_mobile_camera_and_detect_colors()
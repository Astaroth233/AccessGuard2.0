import cv2
import base64

def capture_face_data():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    face_img = None

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Face Capture', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            if len(faces) > 0:
                x, y, w, h = faces[0]  # Capture the first detected face
                face_img = gray[y:y + h, x:x + w]
                break
        elif key == ord('c'):
            face_img = None
            break

    cap.release()
    cv2.destroyAllWindows()

    if face_img is not None:
        _, buffer = cv2.imencode('.jpg', face_img)
        face_data = base64.b64encode(buffer).decode('utf-8')
        return face_data
    return None

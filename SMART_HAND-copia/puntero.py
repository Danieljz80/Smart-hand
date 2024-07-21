import cv2
import mediapipe as mp
import pyautogui
import time

# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5
)

# Configurar la captura de video desde la cámara
cap = cv2.VideoCapture(0)

# Obtener las dimensiones de la pantalla
screen_width, screen_height = pyautogui.size()

# Definir variables para clics, posición inicial del dedo índice, sensibilidad, estado del clic y tiempo de clic sostenido
click_counter = 0
prev_finger_tip_x = 0
prev_finger_tip_y = 0
sensitivity = 0.5  # Ajustar sensibilidad (entre 0 y 1)
click_state = 0  # 0: Sin clic, 1: Clic simple, 2: Doble clic, 3: Clic sostenido
click_start_time = 0  # Tiempo de inicio del clic sostenido

while True:
    # Leer fotograma
    ret, frame = cap.read()

    # Invertir la imagen horizontalmente para una visualización espejo
    frame = cv2.flip(frame, 1)

    # Convertir a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Procesar frame con MediaPipe Hands
    results = hands.process(frame_rgb)

    # Si se detecta una mano:
    if results.multi_hand_landmarks:
        # Obtener la posición del dedo índice
        index_finger_tip = results.multi_hand_landmarks[0].landmark[8]

        # Convertir coordenadas a pantalla
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y * screen_height)

        # Mover el cursor
        pyautogui.moveTo(x, y)

        # Detección de clic con dedo índice hacia abajo
        if index_finger_tip.z < 0.5:
            # Clic simple
            if click_state == 0:
                click_state = 1
                click_counter += 1
                pyautogui.click()
                print("Clic izquierdo")
                click_start_time = time.time()  # Iniciar temporizador para clic sostenido

            # Doble clic (si se levanta y baja rápidamente el dedo)
            elif click_state == 1 and time.time() - click_start_time < 0.3:
                click_state = 0
                click_counter = 0
                pyautogui.doubleClick()
                print("Doble clic")

        # Clic sostenido (si se mantiene el dedo presionado)
        elif click_state == 1:
            click_counter += 1
            duration = time.time() - click_start_time
            print(f"Clic sostenido: {duration:.2f} s")

        # Detectar "doble clic" levantando y bajando el dedo índice rápidamente
        elif click_state == 2 and index_finger_tip.z > 0.5:
            click_state = 0
            click_counter = 0
            print("Doble clic")
            pyautogui.doubleClick()

        # Detectar movimiento horizontal para "arrastrar"
        if prev_finger_tip_x != 0 and prev_finger_tip_y != 0:
            dx = (x - prev_finger_tip_x) * sensitivity
            dy = (y - prev_finger_tip_y) * sensitivity
            pyautogui.drag(dx, dy)
            print(f"Arrastrando: {dx}, {dy}")

        # Actualizar posición anterior del dedo índice
        prev_finger_tip_x = x
        prev_finger_tip_y = y

        # Manejo del estado del clic
        if click_state == 1 and index_finger_tip.z > 0.5:
            click_state = 0
            click_counter = 0

    # Mostrar frame
    cv2.imshow('Control del cursor y funciones del mouse', frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la captura de video y cerrar todas las ventanas
cap.release()

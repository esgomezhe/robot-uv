import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import imutils
import time
from detectors import ObjectDetectors

class SCADAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Sistema SCADA micro PFAL Germinator')
        self.root.config(bg='#000000')
        self.root.geometry('800x480')

        self.cap = cv2.VideoCapture(0)
        self.detectors = ObjectDetectors()
        self.avg_frame = None

        # Crear elementos de la interfaz
        self.create_widgets()

        # Iniciar la actualización de la interfaz
        self.update_frame()

    def create_widgets(self):
        # Botón de Sincronización
        BotonSyncDate = tk.Button(self.root, text="Tx", command=self.sync_date,  bg='black', bd=0, highlightbackground='#21FBFE', highlightthickness=2, relief="solid", fg='white', font=("Helvetica", 10))
        BotonSyncDate.place(x=760, y=2, width=40, height=18)

        # Frame Status Comm
        StatusCommFrame = tk.Frame(self.root, width=800, height=20, background='black', bd=0, highlightbackground='#21FBFE', highlightthickness=2, relief="solid")
        StatusCommFrame.place(x=0, y=460)

        LabelRx = tk.Label(StatusCommFrame, text='label prueba', bd=0, bg='black', fg='white', font=("Helvetica", 10), anchor="w")
        LabelRx.place(x=0, y=0, width=400, height=16)

        # Imagen donde se muestra el video
        self.Imagen = tk.Label(self.root)
        self.Imagen.place(x=200, y=10, width=400, height=400)

    def sync_date(self):
        pass  # Implementar la lógica si es necesario

    def update_frame(self):
        ret, img = self.cap.read()

        if not ret:
            print("No se pudo capturar la imagen.")
            return

        img = cv2.flip(img, 1)  # Voltear la imagen horizontalmente
        gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

        # Inicializar o actualizar el frame promedio para detección de movimiento
        if self.avg_frame is None:
            self.avg_frame = gray_frame.astype("float")
        else:
            cv2.accumulateWeighted(gray_frame, self.avg_frame, 0.05)
            frame_delta = cv2.absdiff(gray_frame, cv2.convertScaleAbs(self.avg_frame))

            # Umbral para la detección de movimiento
            thresh = cv2.threshold(frame_delta, 50, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = imutils.grab_contours(contours)

            for contour in contours:
                if cv2.contourArea(contour) < 6000:  # Ajustado para evitar movimientos pequeños
                    continue

                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, "Movimiento", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Detectar diferentes objetos
        faces = self.detectors.detect_faces(gray_frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, "Rostro", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        eyes = self.detectors.detect_eyes(gray_frame)
        for (x, y, w, h) in eyes:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(img, "Ojo", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        bodies = self.detectors.detect_bodies(gray_frame)
        for (x, y, w, h) in bodies:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Cuerpo", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Convertir la imagen a un formato que tkinter pueda manejar
        cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        im = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=im)
        self.Imagen.configure(image=imgtk)
        self.Imagen.image = imgtk

        # Actualizar el frame cada 10ms
        self.root.after(10, self.update_frame)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.cap.release()
            self.root.destroy()
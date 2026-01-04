# app.py
from dash import Dash
from dashboard import layout, register_callbacks
import threading
import time
import serial
from firebase_config import db
from firebase_admin import firestore

app = Dash(__name__)
app.layout = layout
register_callbacks(app)

# --- Serial reading function ---
def read_serial_and_save():
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    print(" En attente des donnes sErie...")

    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue

     

        try:
            if "Humidity:" in line and "Temperature:" in line:
                humidite = float(line.split("Humidity:")[1].split()[0])
                temperature = float(line.split("Temperature:")[1].split()[0])
                timestamp = firestore.SERVER_TIMESTAMP

                db.collection("donne_dh11").document("temp_hum").set({
                    "humidite": humidite,
                    "temperature": temperature,
                    "timestamp": timestamp
                }, merge=True)

           
                db.collection("donne_dh11_history").add({
                    "humidite": humidite,
                    "temperature": temperature,
                    "timestamp": timestamp
                })

                

        except Exception as e:
            print(" ERREUR :", e)

        time.sleep(2)


threading.Thread(target=read_serial_and_save, daemon=True).start()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=8050)

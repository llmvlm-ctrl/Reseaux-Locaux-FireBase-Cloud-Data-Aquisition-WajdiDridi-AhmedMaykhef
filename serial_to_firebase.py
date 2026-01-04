import serial
import time
from firebase_config import db
from firebase_admin import firestore

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

print(" En attente des donnes serie...")

while True:
    line = ser.readline().decode('utf-8', errors='ignore').strip()
    if not line:
        continue

    print("Reu :", line)

    try:
        if "Humidite:" in line and "Temperature:" in line:
            humidite = float(line.split("Humidite:")[1].split()[0])
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

            print(" CRITURE FIRESTORE OK ", humidite, temperature)

    except Exception as e:
        print(" ERREUR :", e)

    time.sleep(2)

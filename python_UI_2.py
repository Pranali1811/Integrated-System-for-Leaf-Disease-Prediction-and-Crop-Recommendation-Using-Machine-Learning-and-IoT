import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
from datetime import datetime  # Proper datetime import
import json


# MQTT Configuration
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
TOPICS = [
    "esp32/sensors/temperature",
    "esp32/sensors/humidity",
    "esp32/sensors/moisture",
    "esp32/sensors/nitrogen",
    "esp32/sensors/phosphorus",
    "esp32/sensors/potassium",
    "esp32/sensors/ph"
]

# Sensor data storage
sensor_data = {
    "temperature": "N/A",
    "humidity": "N/A",
    "soil_moisture": "N/A",
    "nitrogen": "N/A",
    "phosphorus": "N/A",
    "potassium": "N/A",
    "ph": "N/A"
}

def update_ui():
    for key, label in labels.items():
        label.config(text=sensor_data[key])

    # Save sensor data to JSON
    try:
        data_to_save = {
            "nitrogen": float(sensor_data["nitrogen"].split()[0]),
            "phosphorus": float(sensor_data["phosphorus"].split()[0]),
            "potassium": float(sensor_data["potassium"].split()[0]),
            "temperature": float(sensor_data["temperature"].split()[0]),
            "humidity": float(sensor_data["humidity"].split()[0]),
            "ph": float(sensor_data["ph"]),
            "rainfall": float(sensor_data["soil_moisture"].split()[0])
        }
        with open("shared_sensor_data.json", "w") as f:
            json.dump(data_to_save, f)
        print("[✓] JSON file written: shared_sensor_data.json")
    except Exception as e:
        print(f"[X] Failed to save sensor data: {e}")

    status_var.set(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    for topic in TOPICS:
        client.subscribe(topic)
    status_var.set("Connected to MQTT broker")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    if topic == "esp32/sensors/temperature":
        sensor_data["temperature"] = f"{payload} °C"
    elif topic == "esp32/sensors/humidity":
        sensor_data["humidity"] = f"{payload} %"
    elif topic == "esp32/sensors/moisture":
        sensor_data["soil_moisture"] = f"{payload} %"
    elif topic == "esp32/sensors/nitrogen":
        sensor_data["nitrogen"] = f"{payload} mg/kg"
    elif topic == "esp32/sensors/phosphorus":
        sensor_data["phosphorus"] = f"{payload} mg/kg"
    elif topic == "esp32/sensors/potassium":
        sensor_data["potassium"] = f"{payload} mg/kg"
    elif topic == "esp32/sensors/ph":
        sensor_data["ph"] = f"{payload}"
    
    update_ui()

# GUI Setup
root = tk.Tk()
root.title("ESP32 Sensor Dashboard")
root.geometry("500x500")

# Create a frame for better organization
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Style configuration
style = ttk.Style()
style.configure("TLabel", font=('Helvetica', 12), padding=5)
style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

# Header
header = ttk.Label(main_frame, text="ESP32 Sensor Readings", style="Header.TLabel")
header.pack(pady=10)

# Create a frame for sensor readings
readings_frame = ttk.Frame(main_frame)
readings_frame.pack(fill=tk.BOTH, expand=True)

# Create labels
labels = {}
for i, (key, value) in enumerate(sensor_data.items()):
    frame = ttk.Frame(readings_frame)
    frame.pack(fill=tk.X, pady=2)
    
    name_label = ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", width=20, anchor="w")
    name_label.pack(side=tk.LEFT)
    
    labels[key] = ttk.Label(frame, text=value, width=15, anchor="w")
    labels[key].pack(side=tk.LEFT)

# Status bar
status_var = tk.StringVar(value="Connecting to MQTT...")
status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Update UI function

# MQTT Client Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def connect_mqtt():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        status_var.set(f"Connection failed: {str(e)}")
        root.after(5000, connect_mqtt)  # Retry after 5 seconds

# Start the connection
connect_mqtt()

# Start the GUI
def on_closing():
    client.loop_stop()
    client.disconnect()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

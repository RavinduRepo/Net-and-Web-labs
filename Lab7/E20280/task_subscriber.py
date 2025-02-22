import paho.mqtt.client as mqtt
import json

# MQTT broker address
BROKER = "test.mosquitto.org"
# topics prefix for task operations
TOPIC_PREFIX = "CO324/tasks/"
# dict. to store tasks
tasks = {}

def on_connect(client, userdata, flags, rc):
    """Callback when the client receives a CONNACK response from the server."""
    print("Connected with result code", rc)
    # Subscribe to all task messages
    client.subscribe(f"{TOPIC_PREFIX}#")

def on_message(client, userdata, msg):
    """Callback when a PUBLISH message is received from the server."""
    global tasks
    # Split the topic to get the operation and task ID
    topic_parts = msg.topic.split("/")
    operation = topic_parts[2]
    task_id = topic_parts[3]
    
    if msg.payload:
        # Parse the JSON payload
        task_data = json.loads(msg.payload)
    
    if operation == "ADD":
        # Add the task to the dictionary
        tasks[task_id] = task_data
        print(f"Task {task_id} added: {task_data}")
    
    elif operation == "DELETE":
        # Delete the task from the dictionary if it exists
        if task_id in tasks:
            del tasks[task_id]
            print(f"Task {task_id} deleted.")
        else:
            print(f"Task {task_id} not found.")

    elif operation == "EDIT":
        # Update the task state if it exists
        if task_id in tasks:
            tasks[task_id]["state"] = task_data["state"]
            print(f"Task {task_id} updated: {tasks[task_id]}")
        else:
            print(f"Task {task_id} not found.")

# Create a new MQTT client instance
client = mqtt.Client()
# Assign the on_connect and on_message callbacks
client.on_connect = on_connect
client.on_message = on_message

# connect to the MQTT broker
client.connect(BROKER, 1883, 60)  # 1883 is the default port for MQTT, 60 is the keepalive interval in seconds

# blosking call that processes network traffic, dispatches callbacks, and handles reconnecting
client.loop_forever()

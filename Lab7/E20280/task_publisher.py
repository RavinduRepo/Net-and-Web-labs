import paho.mqtt.client as mqtt
import json
import sys

# MQTT broker address
BROKER = "test.mosquitto.org"
# Topic prefix for task operations
TOPIC_PREFIX = "CO324/tasks/"

def publish_task(operation, task_id, task_data=None):
    """ Publishes a task to an MQTT broker."""

    # creates a new MQTT client instance
    client = mqtt.Client()
    # connects to the MQTT broker
    client.connect(BROKER, 1883, 60)  # 1883 is the default port for MQTT, 60 is the keepalive interval in seconds

    # Construct the topic string
    topic = f"{TOPIC_PREFIX}{operation}/{task_id}"
    # converts the task data to JSON string if provided
    payload = json.dumps(task_data) if task_data else ""

    # publishes the message to the specified topic with QoS level 1
    client.publish(topic, payload, qos=1)
    # Disconnect from the broker
    client.disconnect()

if __name__ == "__main__":
    # Check if the required arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python task_publisher.py <operation> <task_id> [description]")
        sys.exit(1)

    #get the operation and task ID from command line arguments
    operation = sys.argv[1].upper()
    task_id = sys.argv[2]
    # creates the task data if description is provided
    task_data = {"id": task_id, "state": "open", "description": sys.argv[3]} if len(sys.argv) > 3 else None

    # publishes the task
    publish_task(operation, task_id, task_data)

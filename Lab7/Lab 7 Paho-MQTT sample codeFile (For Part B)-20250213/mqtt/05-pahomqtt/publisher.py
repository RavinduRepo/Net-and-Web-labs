import sys
import paho.mqtt.client as mqtt

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# client.connect("mqtt.eclipse.org", 1883, 60)
client.connect("test.mosquitto.org", 1883, 60)

client.loop_start()

infot = client.publish("CO324/chat", sys.argv[1], qos=2)

infot.wait_for_publish()
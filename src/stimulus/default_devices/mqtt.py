import stimulus.device as device
import paho.mqtt.client as paho
import threading

_default_settings = {"transport": "tcp", "tls": False}


class mqtt(device.device):
    def __init__(self, settings):
        super().__init__()
        self.settings = dict(_default_settings, **settings)
        self._lock = threading.Lock()
        # Setup user access
        self.state = device.sprop(False)
        self.running = device.sprop(True)
        self.connect = device.user_function(self.connect)
        self.disconnect = device.user_function(self.disconnect)
        self.publish = device.user_function(self.publish)
        self.on_topic = device.stimulator(self.topic_register, self.topic_cancel)
        self.on_disconnected = device.simple_stimulator()
        self.on_connected = device.simple_stimulator()

        # Setup paho mqtt client
        self._client = paho.Client(transport=self.settings["transport"])
        if self.settings["tls"]:
            self._client.tls_set_context()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self.logger.info(
            f"Connecting to MQTT server {self.settings['host']}:{self.settings['port']}"
        )
        self._client.connect(self.settings["host"], self.settings["port"], 60)
        self._client.loop_start()
        self._handlers = {}

    #        self.on_topic = stimulus.device.stimulator(self._register, self._cancel)

    def start(self):
        self.logger.info("Starting MQTT client")

    def connect(self):
        if not self.running:
            self._client.loop_start()
            self.running.set(True)

    def disconnect(self):
        if self.running:
            self._client.disconnect()
            self.running.set(False)

    def publish(self, topic, payload=None, qos=0, retain=False):
        if self.running:
            self._client.publish(topic, payload, qos, retain)

    def topic_register(self, action, topic):
        self.logger.debug(f"registering for topic {topic} with {action}")
        self._lock.acquire()
        if topic in self._handlers:
            self._lock.release()
            self._handlers[topic].append(action)
        else:
            self._handlers[topic] = list()
            self._lock.release()
            self._handlers[topic].append(action)

            def callback(client, userdata, message):
                self._on_message_topic(topic, message)

            self._client.message_callback_add(topic, callback)
            self._client.subscribe(topic)
            self.logger.debug(f"Subscribed to {topic}")

    def topic_cancel(self, action):
        self._lock.acquire()
        for topic, action_list in self._handlers.items():
            if action in action_list:
                action_list.remove(action)
                break
        if not action_list:  # if action list is empty, remove it
            self._client.unsubscribe(topic)
            del self._handlers[topic]
            self.logger.debug(f"Unsubscribed from {topic} because no action needs it.")
        self._lock.release()

    def _on_connect(self, client, userdate, flags, rc):
        self.logger.debug("Connected to MQTT server with result code " + str(rc))

    def _on_message(self, client, userdata, message):
        self.logger.error("Handling topic with default callback: " + message.topic)

    def _on_message_topic(self, topic, message):
        if topic in self._handlers:
            for action in self._handlers[topic]:
                action.call(message)
        else:
            self.logger.error("Handling topic: " + topic + " " + message.topic)

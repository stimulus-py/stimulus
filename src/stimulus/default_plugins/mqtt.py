import stimulus.device as device
from stimulus.device import logger
import paho.mqtt.client as paho



@device.device_type('mqtt')
class mqtt(device.device):
    def __init__(self,config):
        #Setup user access
        self.state = device.sprop(False)
        self.connect = device.user_function(self.user_connect)
#        self.disconnect = device.user_action(self.user_disconnect)
#        self.send = device.user_action(self.user_send)
        self.on_topic = device.stimulator(self._topic_register, self._topic_cancel)
#        self.on_disconnected = device.simple_stimulator()
#        self.on_connected = device.simple_stimulator()

        #Setup paho mqtt client
        self._client = paho.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        logger.info(f"Connecting to MQTT server {config['host']}:{config['port']}")
        self._client.connect(config['host'],config['port'],60)
        self._client.loop_start()
        self._handlers = {}

#        self.on_topic = stimulus.device.stimulator(self._register, self._cancel)

    def start(self):
        logger.info("Starting MQTT client")
        
    def user_connect(self, message):
        logger.debug(f"Called user_connect {message}")
    
    def _topic_register(self,action, topic):
        logger.debug(f'registering for topic {topic} with {action}')
        if topic in self._handlers:
            self._handlers[topic].append(action)
        else:
            self._handlers[topic] = list()
            self._handlers[topic].append(action)
            def callback(client, userdata, message):
                self._on_message_topic(topic, message)
            self._client.message_callback_add(topic, callback)
            self._client.subscribe(topic)
        
    def _topic_cancel(self,action):
        logger.debug(f'on_topic_cancel')

    def _on_connect(self,client, userdate,flags, rc):
        logger.debug("Connected to MQTT server with result code "+str(rc))

    def _on_message(self,client, userdata, message):
        logger.error("Handling topic with default callback: "+message.topic)
    
    def _on_message_topic(self, topic, message):
        if topic in self._handlers:
            for action in self._handlers[topic]:
                action.call(message)
        else:
            logger.error("Handling topic: "+topic+" "+message.topic)

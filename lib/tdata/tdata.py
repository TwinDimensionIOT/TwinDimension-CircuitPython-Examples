# SPDX-FileCopyrightText: 2023 Luis Pichio for TwinDimension
#
# SPDX-License-Identifier: MIT

"""
`tdata`
================================================================================

A CircuitPython library for communicating with TData.

* Author(s): Luis Pichio for TwinDimension
             Brent Rubell for Adafruit Industries (Adafruit IO -> Initial implementation)
             
             
Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
    https://github.com/adafruit/circuitpython/releases
"""
import time
import json
import re

try:
    from typing import List, Any, Callable, Optional
except ImportError:
    pass

from adafruit_minimqtt.adafruit_minimqtt import MMQTTException
from tdata.tdata_errors import (
    TData_RequestError,
    TData_ThrottleError,
    TData_MQTTError,
)

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/TwinDimensionIOT/TwinDimension-CircuitPython-TData"

class TData_MQTT_Gateway:
    """
    Client for interacting with TData MQTT Gateway API.
    https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api

    :param MiniMQTT mqtt_client: MiniMQTT Client object.
    """

    # pylint: disable=protected-access
    def __init__(self, mqtt_client):
        # Check for MiniMQTT client
        mqtt_client_type = str(type(mqtt_client))
        if "MQTT" in mqtt_client_type:
            self._client = mqtt_client
        else:
            raise TypeError(
                "This class requires a MiniMQTT client object, please create one."
            )
        # TData MQTT API MUST require a username
        try:
            self._user = self._client._username
        except Exception as err:
            raise TypeError(
                "TData requires a username, please set one in MiniMQTT"
            ) from err
        # User-defined MQTT callback methods must be init'd to None
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.on_subscribe = None
        self.on_unsubscribe = None
        self.on_rpc = None
        
        # MQTT event callbacks
        self._client.on_connect = self._on_connect_mqtt
        self._client.on_disconnect = self._on_disconnect_mqtt
        self._client.on_message = self._on_message_mqtt
        self._client.on_subscribe = self._on_subscribe_mqtt
        self._client.on_unsubscribe = self._on_unsubscribe_mqtt
        self._connected = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.disconnect()

    def reconnect(self):
        """Attempts to reconnect to the TData MQTT Broker."""
        try:
            self._client.reconnect()
        except Exception as err:
            raise TData_MQTTError("Unable to reconnect to TData.") from err

    def connect(self):
        """Connects to the TData MQTT Broker.
        Must be called before any other API methods are called.
        """
        try:
            self._client.connect()
        except Exception as err:
            raise TData_MQTTError("Unable to connect to TData.") from err

    def disconnect(self):
        """Disconnects from TData MQTT Broker."""
        if self._connected:
            self._client.disconnect()

    @property
    def is_connected(self):
        """Returns if connected to TData MQTT Broker."""
        try:
            return self._client.is_connected()
        except MMQTTException:
            return False

    # pylint: disable=not-callable, unused-argument
    def _on_connect_mqtt(self, client, userdata, flags, return_code):
        """Runs when the client calls on_connect."""
        if return_code == 0:
            self._connected = True
        else:
            raise TData_MQTTError(return_code)
        # Call the user-defined on_connect callback if defined
        if self.on_connect is not None:
            self.on_connect(self)

    # pylint: disable=not-callable, unused-argument
    def _on_disconnect_mqtt(self, client, userdata, return_code):
        """Runs when the client calls on_disconnect."""
        self._connected = False
        # Call the user-defined on_disconnect callblack if defined
        if self.on_disconnect is not None:
            self.on_disconnect(self)

    # pylint: disable=not-callable
    def _on_message_mqtt(self, client, topic: str, payload: str):
        """Runs when the client calls on_message. Parses and returns
        incoming data from TData feeds.

        :param MQTT client: A MQTT Client Instance.
        :param str topic: MQTT topic response from TData.
        :param str payload: MQTT payload data response from TData.
        """
        topic_tokens = topic.split("/")
        payload_object = json.loads(payload)
        
        if self.on_rpc is not None and topic_tokens[2] == "rpc":
            self.on_rpc(self, payload_object['device'], payload_object['data']['id'], payload_object['data']['method'], payload_object['data']['params'])
            
        if self.on_message is not None:
            self.on_message(self, topic, payload_object)
   
    # pylint: disable=not-callable
    def _on_subscribe_mqtt(self, client, user_data, topic, qos):
        """Runs when the client calls on_subscribe."""
        if self.on_subscribe is not None:
            self.on_subscribe(self, user_data, topic, qos)

    # pylint: disable=not-callable
    def _on_unsubscribe_mqtt(self, client, user_data, topic, pid):
        """Runs when the client calls on_unsubscribe."""
        if self.on_unsubscribe is not None:
            self.on_unsubscribe(self, user_data, topic, pid)

    def loop(self, timeout=1):
        """Manually process messages from TData.
        Call this method to check incoming subscription messages.

        :param int timeout: Socket timeout, in seconds.

        Example usage of polling the message queue using loop.

        .. code-block:: python

            while True:
                io.loop()
        """
        self._client.loop(timeout)

    def device_connect(
        self,
        device_name: str = None,
    ):
        """Device Connect API
        Once received, T>Data will lookup or create a device with the name specified.
        Also, T>Data will publish messages about new attribute updates and RPC commands
        for a particular device to this Gateway
        """
        if device_name is not None:
            data = { "device": device_name }
            self._client.publish("v1/gateway/connect", json.dumps(data))
        else:
            raise TData_MQTTError("Must provide a device_name.")
    
    def device_disconnect(
        self,
        device_name: str = None,
    ):
        """Device Disconnect API
        Once received, T>Data will no longer publish updates for this particular device
        to this Gateway.
        """
        if device_name is not None:
            data = { "device": device_name }
            self._client.publish("v1/gateway/disconnect", json.dumps(data))
        else:
            raise TData_MQTTError("Must provide a device_name.")

                
    def publish(
        self,
        publish_type: str = "telemetry",
        data: dict = None,
    ):
        """Telemetry upload / Attributes API 
        Publishes telemetry / attributes to T>Data.
        """
        self._client.publish("v1/gateway/{0}".format(publish_type), json.dumps(data))
        
    def subscribe_to_rpcs(
        self
    ):
        """RPC API
        Server-side RPC.

        :param str device: Device name.

        """
        self._client.subscribe("v1/gateway/rpc")
                
    def rpc_response(
        self,
        device_name: str = None,
        rpc_id: int = None,
        data: dict = None,        
    ):
        """RPC API
        RPC response.

        :param str device: Device name.
        :param int rpc_id: RPC id (received).
        :param dict data: RPC response.

        """
        self._client.subscribe("v1/gateway/rpc")
        data = { "device": device_name, "id": rpc_id, "data": data }
        self._client.publish("v1/gateway/rpc", json.dumps(data))
        
class TData_MQTT:
    """
    Client for interacting with TData MQTT device API.
    https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api

    :param MiniMQTT mqtt_client: MiniMQTT Client object.
    """

    # pylint: disable=protected-access
    def __init__(self, mqtt_client):
        # Check for MiniMQTT client
        mqtt_client_type = str(type(mqtt_client))
        if "MQTT" in mqtt_client_type:
            self._client = mqtt_client
        else:
            raise TypeError(
                "This class requires a MiniMQTT client object, please create one."
            )
        # TData MQTT API MUST require a username
        try:
            self._user = self._client._username
        except Exception as err:
            raise TypeError(
                "TData requires a username, please set one in MiniMQTT"
            ) from err
        # User-defined MQTT callback methods must be init'd to None
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.on_subscribe = None
        self.on_unsubscribe = None
        self.on_rpc = None
        
        # MQTT event callbacks
        self._client.on_connect = self._on_connect_mqtt
        self._client.on_disconnect = self._on_disconnect_mqtt
        self._client.on_message = self._on_message_mqtt
        self._client.on_subscribe = self._on_subscribe_mqtt
        self._client.on_unsubscribe = self._on_unsubscribe_mqtt
        self._connected = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.disconnect()

    def reconnect(self):
        """Attempts to reconnect to the TData MQTT Broker."""
        try:
            self._client.reconnect()
        except Exception as err:
            raise TData_MQTTError("Unable to reconnect to TData.") from err

    def connect(self):
        """Connects to the TData MQTT Broker.
        Must be called before any other API methods are called.
        """
        try:
            self._client.connect()
        except Exception as err:
            raise TData_MQTTError("Unable to connect to TData.") from err

    def disconnect(self):
        """Disconnects from TData MQTT Broker."""
        if self._connected:
            self._client.disconnect()

    @property
    def is_connected(self):
        """Returns if connected to TData MQTT Broker."""
        try:
            return self._client.is_connected()
        except MMQTTException:
            return False

    # pylint: disable=not-callable, unused-argument
    def _on_connect_mqtt(self, client, userdata, flags, return_code):
        """Runs when the client calls on_connect."""
        if return_code == 0:
            self._connected = True
        else:
            raise TData_MQTTError(return_code)
        # Call the user-defined on_connect callback if defined
        if self.on_connect is not None:
            self.on_connect(self)

    # pylint: disable=not-callable, unused-argument
    def _on_disconnect_mqtt(self, client, userdata, return_code):
        """Runs when the client calls on_disconnect."""
        self._connected = False
        # Call the user-defined on_disconnect callblack if defined
        if self.on_disconnect is not None:
            self.on_disconnect(self)

    # pylint: disable=not-callable
    def _on_message_mqtt(self, client, topic: str, payload: str):
        """Runs when the client calls on_message. Parses and returns
        incoming data from TData feeds.

        :param MQTT client: A MQTT Client Instance.
        :param str topic: MQTT topic response from TData.
        :param str payload: MQTT payload data response from TData.
        """
        topic_tokens = topic.split("/")
        payload_object = json.loads(payload)
        
        if self.on_rpc is not None and topic_tokens[3] == "rpc":
            self.on_rpc(self, int(topic_tokens[5]), payload_object['method'], payload_object['params'])
        
        if self.on_message is not None:
            self.on_message(self, topic, payload_object)
   
    # pylint: disable=not-callable
    def _on_subscribe_mqtt(self, client, user_data, topic, qos):
        """Runs when the client calls on_subscribe."""
        if self.on_subscribe is not None:
            self.on_subscribe(self, user_data, topic, qos)

    # pylint: disable=not-callable
    def _on_unsubscribe_mqtt(self, client, user_data, topic, pid):
        """Runs when the client calls on_unsubscribe."""
        if self.on_unsubscribe is not None:
            self.on_unsubscribe(self, user_data, topic, pid)

    def loop(self, timeout=1):
        """Manually process messages from TData.
        Call this method to check incoming subscription messages.

        :param int timeout: Socket timeout, in seconds.

        Example usage of polling the message queue using loop.

        .. code-block:: python

            while True:
                io.loop()
        """
        self._client.loop(timeout)
               
    def publish(
        self,
        publish_type: str = "telemetry",
        data: dict = None,
    ):
        """Telemetry upload / Attributes API 
        Publishes telemetry / attributes to T>Data.
        """
        self._client.publish("v1/devices/me/{}".format(publish_type), json.dumps(data))

    def subscribe_to_rpcs(
        self
    ):
        """RPC API
        Server-side RPC.

        """
        self._client.subscribe("v1/devices/me/rpc/request/+")
                
    def rpc_response(
        self,
        request_id: int = None,
        data: dict = None,        
    ):
        """RPC API
        RPC response.

        :param str device: Device name.
        :param int rpc_id: RPC id (received).
        :param dict data: RPC response.

        """
        self._client.publish("v1/devices/me/rpc/response/{}".format(request_id), json.dumps(data))


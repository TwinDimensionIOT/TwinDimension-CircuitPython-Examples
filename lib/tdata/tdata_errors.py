# SPDX-FileCopyrightText: 2023 Luis Pichio for TwinDimension
#
# SPDX-License-Identifier: MIT

"""
`tdata_errors.py`
======================================================
CircuitPython T>DATA Error Classes
* Author(s): Luis Pichio for TwinDimension
             Brent Rubell for Adafruit Industries (Adafruit IO -> Initial implementation)
"""


class TData_ThrottleError(Exception):
    """TData request error class for rate-limiting."""


class TData_RequestError(Exception):
    """TData request error class"""

    def __init__(self, response):
        response_content = response.json()
        error = response_content["error"]
        super().__init__(
            "TData Error {0}: {1}".format(response.status_code, error)
        )


class TData_MQTTError(Exception):
    """TData MQTT error class"""

    def __init__(self, response):
        super().__init__("MQTT Error: {0}".format(response))

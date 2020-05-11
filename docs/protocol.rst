.. Copyright 2020, NTRobotics

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

.. _protocol-description:

Протокол
========

Навигационный блок поддерживает протокол MAVLink_ версии 1.0 и 2.0.

.. _MAVLink: https://mavlink.io/

Поддерживаемые сообщения
------------------------

Исходящие сообщения
~~~~~~~~~~~~~~~~~~~

* HEARTBEAT_ – сигнал о присутствии блока в системе
* SYS_STATUS_ – состояние навигационного блока
* PARAM_VALUE_ – значение параметра
* GLOBAL_POSITION_INT_ – GPS-координаты ЛА (только в режиме локализации)
* GPS_GLOBAL_ORIGIN_ – GPS-координаты локальной системы отсчёта
* COMMAND_ACK_ – ответ на команду (см. `Поддерживаемые команды`_)
* VISION_POSITION_ESTIMATE_ – координаты в локальной системе отсчёта (NED)
* FILE_TRANSFER_PROTOCOL_ – передача карт
* DISTANCE_SENSOR_ – расстояние до поверхности
* AUTOPILOT_VERSION_ – версия программного обеспечения
* STATUSTEXT_ – различные служебные сообщения

Входящие сообщения
~~~~~~~~~~~~~~~~~~

* HEARTBEAT_ – сигнал о присутствии мастера
* PARAM_REQUEST_READ_ – запрос значения параметра
* PARAM_REQUEST_LIST_ – запрос списка параметров
* PARAM_SET_ – изменить значение параметра
* ATTITUDE_ – ориентация ЛА (NED)
* GLOBAL_POSITION_INT_ – GPS-координаты ЛА (только в режиме картирования)
* COMMAND_INT_ – команда (см. `Поддерживаемые команды`_)
* COMMAND_LONG_ – команда (см. `Поддерживаемые команды`_)
* FILE_TRANSFER_PROTOCOL_ – передача карт

.. _`Поддерживаемые команды`:

Поддерживаемые команды (MAV_CMD_)
---------------------------------

* MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN_ – выключить или перезагрузить блок
* MAV_CMD_SET_MESSAGE_INTERVAL_ – установить интервал между сообщениями
* MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES_ – запрос версии программного обеспечения

Поддерживаемы микросервисы
--------------------------

* `Heartbeat/Connection Protocol <https://mavlink.io/en/services/heartbeat.html>`_
* `Parameter Protocol <https://mavlink.io/en/services/parameter.html>`_
* `Command Protocol <https://mavlink.io/en/services/command.html>`_
* `File Transfer Protocol <https://mavlink.io/en/services/ftp.html>`_

Подробное описание микросервисов см. в Приложении 2.

.. _HEARTBEAT: https://mavlink.io/en/messages/common.html#HEARTBEAT
.. _SYS_STATUS: https://mavlink.io/en/messages/common.html#SYS_STATUS
.. _PARAM_VALUE: https://mavlink.io/en/messages/common.html#PARAM_VALUE
.. _GLOBAL_POSITION_INT: https://mavlink.io/en/messages/common.html#GLOBAL_POSITION_INT
.. _GPS_GLOBAL_ORIGIN: https://mavlink.io/en/messages/common.html#GPS_GLOBAL_ORIGIN
.. _COMMAND_ACK: https://mavlink.io/en/messages/common.html#COMMAND_ACK
.. _VISION_POSITION_ESTIMATE: https://mavlink.io/en/messages/common.html#VISION_POSITION_ESTIMATE
.. _FILE_TRANSFER_PROTOCOL: https://mavlink.io/en/messages/common.html#FILE_TRANSFER_PROTOCOL
.. _DISTANCE_SENSOR: https://mavlink.io/en/messages/common.html#DISTANCE_SENSOR
.. _AUTOPILOT_VERSION: https://mavlink.io/en/messages/common.html#AUTOPILOT_VERSION
.. _STATUSTEXT: https://mavlink.io/en/messages/common.html#STATUSTEXT
.. _PARAM_REQUEST_READ: https://mavlink.io/en/messages/common.html#PARAM_REQUEST_READ
.. _PARAM_REQUEST_LIST: https://mavlink.io/en/messages/common.html#PARAM_REQUEST_LIST
.. _PARAM_SET: https://mavlink.io/en/messages/common.html#PARAM_SET
.. _ATTITUDE: https://mavlink.io/en/messages/common.html#ATTITUDE
.. _COMMAND_INT: https://mavlink.io/en/messages/common.html#COMMAND_INT
.. _COMMAND_LONG: https://mavlink.io/en/messages/common.html#COMMAND_LONG

.. _MAV_CMD: https://mavlink.io/en/messages/common.html#mav_commands

.. _MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN: https://mavlink.io/en/messages/common.html#MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN
.. _MAV_CMD_SET_MESSAGE_INTERVAL: https://mavlink.io/en/messages/common.html#MAV_CMD_SET_MESSAGE_INTERVAL
.. _MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES: https://mavlink.io/en/messages/common.html#MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES
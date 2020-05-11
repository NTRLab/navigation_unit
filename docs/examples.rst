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

Примеры использования
=====================

Простые действия
----------------

* ``view_params.py`` – просмотр параметров
* ``set_params.py`` – будут отображены текущие параметры, а затем предложено изменить значение любого из них
* ``reboot.py`` – перезагрузка навигационного блока
* ``shutdown.py`` – завершение работы навигационного блока
* ``download_file.py`` – выгрузка карты из навигационного блока. Будет выведен список карт, хранящихся в памяти |НБ|, а затем будет предложено скачать любую из них
* ``upload_file.py`` – загрузка карты в навигационный блок. Будет предложено ввести путь к файлу на локальной машине, затем — путь, по которому нужно сохранить файл в памяти |НБ|
* ``disable_vision.py`` – отключение вывода координат

Демонстрация режимов работы
---------------------------

Навигационный блок имеет параметр высота инициализации.
После включения |НБ| сопособен выдавать только высоту над поверхностью, пока не достигнет высоты *инициализации* (параметр |INIT_ALT|).
Во всех нижеприведённых примерах высота *инициализации* составляет 1 метр.

* ``view_vision_position.py`` – отображение локальных координат.
  |НБ| будет настроен на режим навигации без карты и перезагружен при необходимости.
  Локальные координаты будут отображаться на экране.
* ``view_global_position.py`` – отображение глобальных координат.
  |НБ| будет настроен на режим навигации без карты и перезагружен при необходимости.
  Глобальные координаты будут отображаться на экране.
  Вычисление текщих глобальных координат производится относительно координат, заданных параметрами :ref:`ORIGIN_LAT<origin_lat_param>`, :ref:`ORIGIN_LON<origin_lon_param>`, :ref:`ORIGIN_ALT<origin_alt_param>`, :ref:`ORIGIN_HDG<origin_hdg_param>`
* ``mapping_mode.py`` – построение карты.
  |НБ| будет настроен на режим навигации с сохранением карты.
  Локальные координаты будут отображаться на экране.
  Сохранение карты в файл произойдёт если в сообщении HEARTBEAT_, поступающем на вход |НБ|, в поле base_mode флаг MAV_MODE_FLAG_SAFETY_ARMED_ перейдёт из состояния 1 в 0, что означает выключение двигателей, либо при перезагрузке или завершении работы.
* ``localization_mode.py`` – определение координат на построенной карте.
  |НБ| будет настроен на режим навигации с готовой картой.
  Локальные координаты будут отображаться на экране.

.. _HEARTBEAT: https://mavlink.io/en/messages/common.html#HEARTBEAT
.. _MAV_MODE_FLAG_SAFETY_ARMED: https://mavlink.io/en/messages/common.html#MAV_MODE_FLAG_SAFETY_ARMED

.. |НБ| replace:: :abbr:`НБ (навигационный блок)`

.. |INIT_ALT| replace:: :ref:`INIT_ALT<init_alt_param>`
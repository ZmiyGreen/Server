import select
import os
from abc import ABC


def unsafe_write(path: str, value) -> None:
    """
    Осуществляет запись значения (value) в файл без предварительной проверки на существование
    :param path : Путь к файлу
    :param value: Значение, которов будет записано
    :return: None
    """
    with open(path, "w") as wr:
        wr.write(str(value))


def check_write(path: str, value) -> None:
    """
    Осуществляет запись значения (value) в файл после проверки на существование. Вызывает исключение если файл не
    существует
    :param path : Путь к файлу
    :param value: Знпачение, которое будет записано
    :return: None
    """
    if not os.path.exists(path):
        raise ValueError
    else:
        with open(path, "w") as wr:
            wr.write(str(value))


def try_write(path: str, value) -> bool:
    """
    Осуществляет запись значения (value) в файл после проверки на существование. Возвращает bool-значение, не вызывает
    исключения
    :param path: Путь к файлу
    :param value: Значение, которое будет записано
    :return:
        True - если файл существует и значение успешно записано
        False - Если файл не существует
    """
    if not os.path.exists(path):
        return False
    else:
        with open(path, "w") as wr:
            wr.write(str(value))
        return True


def gpio_exists(gpio_line) -> bool:
    """
    Проверяет экспортирована ли gpio - линия соответствующая указанному аргументу (gpio_line)
    :param gpio_line: gpio - линия для которой осуществляется проверка
    :return:
        True - если линия экспортирована
        False - если линия не экспортирована (файл не существует)
    """
    if os.path.exists(f"/sys/class/gpio/gpio{gpio_line}"):
        return True
    else:
        return False


def gpio_export(gpio_line) -> None:
    """
    Осуществляет экспорт gpio - линии соответствующий указанному аргументу (gpio_line)
    :param gpio_line:
    """
    if gpio_exists(gpio_line):
        raise ValueError
    else:
        unsafe_write(f"/sys/class/gpio/export", gpio_line)


def gpio_unexport(gpio_line) -> None:
    """
    Отменяет экспорт gpio - линии соответствующий указанному аргументу (gpio_line)
    """
    if not gpio_exists(gpio_line):
        raise ValueError
    else:
        unsafe_write(f"/sys/class/gpio/unexport", gpio_line)


def gpio_try_open(gpio_line: int, direction: str = 'in', edge: str = None) -> bool:
    """
    Экспортирует gpio - линию (gpio_line), с заданными показателями direction и edge. возвращает True в случае
    успешного экспорта, иначе - False. Не вызывает исключений.
    """
    if gpio_exists(gpio_line):
        return False
    else:
        if direction not in ['in', 'out'] or edge not in ['both', 'falling', 'rising', 'none', None]:
            raise ValueError
        else:
            gpio_export(gpio_line)
            unsafe_write(f"/sys/class/gpio/gpio{gpio_line}/direction", direction)
            if edge is not None:
                check_write(f"/sys/class/gpio/gpio{gpio_line}/edge", edge)
        return True


def gpio_open(gpio_line: int, direction: str = 'in', edge: str = None) -> bool:
    """
    Экспортирует gpio - линию (gpio_line), с заданными показателями direction и edge.
    """
    if direction not in ['in', 'out'] or edge not in ['both', 'falling', 'rising', 'none', None]:
        raise ValueError
    else:
        gpio_export(gpio_line)
        unsafe_write(f"/sys/class/gpio/gpio{gpio_line}/direction", direction)
        if edge is not None:
            check_write(f"/sys/class/gpio/gpio{gpio_line}/edge", edge)


def gpio_try_close(gpio_line, off_value=False) -> bool:
    """
    Отменяет экспорт gpio - линию (gpio_line). возвращает True в случае успешного экспорта, иначе - False.
    Не вызывает исключений.
    """
    if not gpio_exists(gpio_line):
        return False
    else:
        if off_value:
            unsafe_write(f"/sys/class/gpio/gpio{gpio_line}/value", 0)
        gpio_unexport(gpio_line)
        return True


def gpio_close(gpio_line, off_value=False) -> None:
    """
    Отменяет экспорт gpio-линии. Если off_value = True перед закрытием gpio-линии меняет соответствующее значение value
    на 0.
    """
    if off_value:
        check_write(f"/sys/class/gpio/gpio{gpio_line}/value", 0)
    gpio_unexport(gpio_line)


class Device(ABC):
    """
    Базовый класс для работы с GPIO
    """
    def __init__(self, gpio_line: int, direction: str = 'in', edge: str = None):
        self.gpio_line = gpio_line
        self.path = f"/sys/class/gpio/gpio{gpio_line}/"
        self.edge = edge
        self.direction = direction
        self.__value = 0

    @property
    def direction(self):
        return self.__direction

    @direction.setter
    def direction(self, var):
        if var in ['in', 'out']:
            self.__direction = var
        else:
            raise ValueError("Invalid direction!")

    @property
    def edge(self):
        return self.__edge

    @edge.setter
    def edge(self, var):
        if var in ['both', 'falling', 'rising', 'none', None]:
            self.__edge = var
        else:
            raise ValueError("Invalid edge!")

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, var):
        if var in [0, 1]:
            self.__value = var
            unsafe_write(f"{self.path}value", self.value)
        else:
            raise ValueError("Invalid value!")

    def open(self):
        gpio_open(self.gpio_line, self.direction, self.edge)

    def close(self):
        gpio_try_close(self.gpio_line)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line}"

    def __str__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line}"


class Led(Device):
    """
    Класс для управления подключенными по gpio светодиодами
    """
    def __init__(self, gpio_line: int, direction: str = 'out', edge: str = None):
        super().__init__(gpio_line, direction, edge)

    def switch(self):
        """
        Переключает состояние светодиода на противоположное -- если включен - выключит, если выключен - включит
        """
        self.value = 1 if self.value == 0 else 0

    def close(self):
        gpio_try_close(self.gpio_line, True)

    def __repr__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line} value : {self.value}"

    def __str__(self):
        return f"Led: GPIO/SYSFSID : {self.gpio_line} value : {self.value}"


class Button(Device):
    """
    Класс для управления подключенными по gpio кнопками
    """
    def __init__(self, gpio_line: int, direction: str = 'in', edge: str = 'rising'):
        super().__init__(gpio_line, direction, edge)

    def click(self) -> bool:
        """
        Пассивное ожидание нажатия кнопки
        :return: Возвращает True если кнопка нажата
        Примечание: в следующей версии будет добавлен возврат False, в случае если кнопка не нажата в течении
        определенного промежутка времени
        """
        with open(f'{self.path}value', 'r') as reader:
            reader.read()
            with select.epoll() as event:
                event.register(reader.fileno(), select.EPOLLPRI)
                event.poll()
                return True

    def __enter__(self):
        self.open()
        return self

    def __str__(self):
        return f"Button GPIO/SYSFSID : {self.gpio_line}"

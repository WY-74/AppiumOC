import os
import time
import random
from typing import List
from datetime import datetime
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.wheel_input import WheelInput


class AppiumOC:
    """
    blacklist: [(self.by.ID, "xxxxxx"), (self.by.XPATH, "xxxxxx")]
    """

    def __init__(self, driver: WebDriver = None):
        self.by = AppiumBy
        self.blacklist = []
        self.driver = driver
        self.log = "/tmp/log"
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.timeout = 5

    def _sleep(self):
        times = random.randint(0, self.timeout)
        print(f"Sleep : {times}")
        time.sleep(times)

    def _elem_center(self, elem: WebDriver):
        location = elem.location
        size = elem.size
        x = location['x'] + size['width'] / 2
        y = location['y'] + size['height'] / 2
        return (x, y)

    def _init_actionchains(self, interaction: str, w3c: bool = False):
        """
        ponter: mouse, touch, pen
        key: key
        wheel: wheel
        """
        _pointer = ["mouse", "touch", "pen"]
        _class = "pointer" if interaction in _pointer else interaction
        _args = [interaction]

        _device_map = {"pointer": PointerInput, "key": KeyInput, "wheel": WheelInput}
        if interaction in _pointer:
            _args.append("mouse")
        ac = ActionChains(self.driver, devices=[_device_map[_class](*_args)])

        if w3c:
            return ac.w3c_actions
        return ac

    def back(self):
        self.driver.back()

    def find_element(self, by: AppiumBy, value: str):
        """
        ACCESSIBILITY_ID(Android): content-desc
        ACCESSIBILITY_ID(iOS): accessibility-id
        """
        try:
            return self.driver.find_element(by=by, value=value)
        except NoSuchElementException as e:
            for black in self.blacklist:
                _elems = self.driver.find_elements(*black)
                if _elems:
                    _elems[0].click()
                    return self.find_element(by=by, value=value)
            raise e

    def find_subelement(self, element: WebDriver, by: AppiumBy, value: str):
        try:
            return element.find_element(by=by, value=value)
        except NoSuchElementException as e:
            for black in self.blacklist:
                _elems = self.driver.find_elements(*black)
                if _elems:
                    _elems[0].click()
                    return self.find_subelement(element=element, by=by, value=value)
            raise e

    def find_elements(self, by: AppiumBy, value: str):
        elems = self.driver.find_elements(by=by, value=value)
        if elems:
            return elems
        for black in self.blacklist:
            _elems = self.driver.find_elements(*black)
            if _elems:
                _elems[0].click()
                return self.find_elements(by=by, value=value)
        return []

    def get_attribute(self, elem: WebDriver | tuple, attr: str):
        if isinstance(elem, tuple):
            elem = self.find_element(*elem)
        try:
            if attr == "text":
                return elem.text
            return elem.get_attribute(attr)
        except NoSuchElementException as e:
            for black in self.blacklist:
                _elems = self.driver.find_elements(*black)
                if _elems:
                    _elems[0].click()
                    return self.get_attribute(elem=elem, attr=attr)
            raise e

    def safeclick(self, elem: WebDriver | tuple):
        if isinstance(elem, tuple):
            elem = self.find_element(*elem)

        if self.get_attribute(elem, "clickable") == "false":
            self.driver.tap([self._elem_center(elem)])
            print("\033[93mClick by tap!\033[0m")
            return True
        elem.click()
        return True

    def multiclick(self, locators: tuple):
        for locator in locators:
            self.safeclick(locator)
        return True

    def touch_with_location(self, x: int, y: int):
        ac = self._init_actionchains("touch", w3c=True)
        ac.pointer_action.move_to_location(x, y).click()
        ac.perform()
        return True

    def send_keys(self, elem: WebDriver | tuple, text: str):
        if isinstance(elem, tuple):
            elem = self.find_element(*elem)
        try:
            elem.send_keys(text)
            return True
        except NoSuchElementException as e:
            for black in self.blacklist:
                _elems = self.driver.find_elements(*black)
                if _elems:
                    _elems[0].click()
                    return self.send_keys(elem=elem, text=text)
            raise e

    def page_source_as_file(self, path):
        try:
            source = self.driver.page_source
            with open(path, "a") as f:
                f.write(source)
            del source
            return True
        except FileNotFoundError:
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                return self.page_source_as_file(path=path)

    def screenshot_as_file(self, path):
        try:
            png = self.driver.get_screenshot_as_png()
            with open(path, "wb") as f:
                f.write(png)
            del png
            return True
        except FileNotFoundError:
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
                return self.screenshot_as_file(path=path)

    def move_to_location_by_touch(self, pointers: List[tuple]):
        """
        pointers: [(175, 247),(175, 983) ,(904, 983)]
        """
        ac = self._init_actionchains("touch", w3c=True)
        ac.pointer_action.move_to_location(*pointers[0])
        ac.pointer_action.pointer_down()

        for location in pointers[1:]:
            ac.pointer_action.move_to_location(*location)
        ac.perform()
        return True

    def switch_to_latest_context(self):
        WebDriverWait(self.driver, self.timeout).until(lambda driver: len(self.driver.contexts) > 1)
        context = self.driver.contexts[-1]
        self.driver.switch_to.context(context)
        return True

    def get(self, url: str):
        self.driver.get(url)
        return True

    def switch_to_latest_window(self):
        WebDriverWait(self.driver, self.timeout).until(lambda driver: len(self.driver.window_handles) > 1)
        window_handles = self.driver.window_handles
        self.driver.switch_to.window(window_handles[-1])
        return True

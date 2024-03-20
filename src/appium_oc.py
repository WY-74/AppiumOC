import os
import time
import random
from typing import List, Dict
from datetime import datetime
from appium import webdriver
from appium.webdriver.webdriver import WebDriver
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement as MobileWebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.wheel_input import WheelInput
from appium_oc.decorator import remove_pop_ups


class AppiumOC:
    """
    blacklist: [(self.by.ID, "xxxxxx"), (self.by.XPATH, "xxxxxx")]
    """

    def __init__(self, driver: WebDriver = None):
        self.driver = driver
        self.by = AppiumBy
        self.blacklist = []
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.timeout = 20

    def remote(self, opts: Dict[str, str | bool], ip: str = "127.0.0.1", port: str = "4723"):
        if self.driver is not None:
            return

        options = AppiumOptions()
        self.driver = webdriver.Remote(f"http://{ip}:{port}", options=options.load_capabilities(opts))
        return True

    def quit(self):
        self.driver.quit()
        return True

    def back(self):
        self.driver.back()

    @remove_pop_ups
    def find_element(self, locator: tuple):
        """
        ACCESSIBILITY_ID(Android): content-desc
        ACCESSIBILITY_ID(iOS): accessibility-id
        """
        return self.driver.find_element(*locator)

    def must_get_element(self, locator: tuple):
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))

    def move_to_find_element(self, locator: tuple, start: tuple, end: tuple):
        return WebDriverWait(self.driver, self.timeout).until(
            self._move_element_presence_in_dom(*locator, start=start, end=end)
        )

    def must_not_element(self, locator: tuple):
        return WebDriverWait(self.driver, self.timeout).until_not(EC.presence_of_element_located(locator))

    def find_elements(self, locator: tuple):
        elems = self.driver.find_elements(*locator)
        if elems:
            return elems
        for black in self.blacklist:
            _elems = self.driver.find_elements(*black)
            if _elems:
                _elems[0].click()
                return self.find_elements(locator)
        return []

    def get_attribute(self, locator: tuple, attr: str):
        elem = self.find_element(locator)
        if attr == "text":
            return elem.text
        return elem.get_attribute(attr)

    def click(self, locator: tuple):
        elem = self.find_element(locator)
        if elem.get_attribute("clickable") == "false":
            self.driver.tap([self._elem_center(elem)])
            return True
        elem.click()
        return True

    def multiclick(self, locators: List[tuple]):
        """
        locators = [(css_selector, "#id"), (css_selector, ".class")]
        """
        for locator in locators:
            self.click(locator)
        return True

    def tap(self, x: int, y: int):
        self.driver.tap([(x, y)])
        return True

    def send_keys(self, locator: tuple, text: str):
        elem = self.find_element(locator)
        elem.send_keys(text)
        return True

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

    def _sleep(self):
        times = random.randint(0, self.timeout)
        print(f"Sleep : {times}")
        time.sleep(times)

    def _elem_center(self, elem: MobileWebElement):
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

    def _move_element_presence_in_dom(self, locator: tuple, start: tuple, end: tuple):
        def _predicate(driver: WebDriver):
            try:
                return driver.find_element(locator)
            except NoSuchElementException:
                self.move_to_location_by_touch([start, end])
                return False

        return _predicate

import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.common.actions.wheel_input import WheelInput


class AppiumOC:
    def __init__(self, driver) -> None:
        self.driver = driver

    def _sleep(self, times: int = 1):
        time.sleep(times)

    def _elem_center(self, elem):
        location = elem.location
        size = elem.size
        x = location['x'] + size['width'] / 2
        y = location['y'] + size['height'] / 2
        return (x, y)

    def _get_visibility_elem(self, value: str, by: str = "XPATH"):
        locator = (getattr(AppiumBy, by), value)
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(locator))

    def _init_actionchains(self, interaction: str):
        """
        ponter: mouse, touch, pen
        key: key
        wheel: wheel
        """
        _pointer = ["mouse", "touch", "pen"]
        _device_map = {"pointer": PointerInput, "key": KeyInput, "wheel": WheelInput}
        if interaction in _pointer:
            return ActionChains(self.driver, devices=[_device_map["pointer"](interaction, "mouse")])

        return ActionChains(self.driver, devices=[_device_map[interaction](interaction)])

    def clear(self, elem):
        elem.clear()
        return True

    def get_elems(self, value: str, by: str = "XPATH", multiple: bool = False):
        """
        ACCESSIBILITY_ID(Android): content-desc
        ACCESSIBILITY_ID(iOS): accessibility-id
        """
        if multiple:
            return self.driver.find_elements(getattr(AppiumBy, by), value)
        return self.driver.find_element(getattr(AppiumBy, by), value)

    def attribute(self, elem, attr: str, by: str = "XPATH"):
        if isinstance(elem, str):
            elem = self.get_elems(elem, by=by)
        return elem.get_attribute(attr)

    def page_source_to_file(self, to: str = "/tmp/source.xml"):
        source = self.driver.page_source
        with open(to, "a+") as f:
            f.write(source)
        return True

    def safeclick(self, elem, by: str = "XPATH"):
        if isinstance(elem, str):
            elem = self._get_visibility_elem(elem, by=by)

        if self.attribute(elem, "clickable") == "false":
            self.driver.tap([self._elem_center(elem)])
            print("\033[93mClick by tap!\033[0m")
            return True
        elem.click()
        return True

    def send(self, elem, text: str, by: str = "XPATH"):
        if isinstance(elem, str):
            elem = self.get_elems(elem, by=by)
        elem.send_keys(text)
        return True

    def multi_click(self, elems: list):
        for elem in elems:
            if isinstance(elem, list):
                kwargs = dict(zip(["elem", "by"], elem))
                self.safeclick(**kwargs)
                continue
            self.safeclick(elem)
        return True

    def move_with_touch(self, s: tuple, e: tuple):
        ac = self._init_actionchains("touch")
        ac.w3c_actions.pointer_action.move_to_location(*s)
        ac.w3c_actions.pointer_action.pointer_down()
        ac.w3c_actions.pointer_action.move_to_location(*e)
        ac.perform()

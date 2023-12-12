import time
from appium.webdriver.common.appiumby import AppiumBy


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

    def clear(self, elem):
        elem.clear()
        return True

    def elems_by_accessibilty(self, id: str, multiple: bool = False):
        """
        Android: content-desc
        iOS: accessibility-id
        """
        if multiple:
            return self.driver.find_elements(AppiumBy.ACCESSIBILITY_ID, id)

        return self.driver.find_element(AppiumBy.ACCESSIBILITY_ID, id)

    def elems_by_xpath(self, xpath: str, multiple: bool = False):
        if multiple:
            return self.driver.find_elements(AppiumBy.XPATH, xpath)

        return self.driver.find_element(AppiumBy.XPATH, xpath)

    def attribute(self, elem, attr: str, by: str = "accessibilty"):
        """by: accessibilty or xpath"""
        if isinstance(elem, str):
            elem = getattr(self, f"elems_by_{by}")(elem)
        return elem.get_attribute(attr)

    def safeclick(self, elem, by: str = "accessibilty"):
        """by: accessibilty or xpath"""
        if isinstance(elem, str):
            elem = getattr(self, f"elems_by_{by}")(elem)
        if self.attribute(elem, "clickable") == "false":
            self.driver.tap([self._elem_center(elem)])
            print("\033[93mClick by tap\033[0m")
            return True
        elem.click()
        return True

    def send(self, elem, text: str, by: str = "accessibilty"):
        """by: accessibilty or xpath"""
        if isinstance(elem, str):
            elem = getattr(self, f"elems_by_{by}")(elem)
        elem.send_keys(text)
        return True

    def multi_click(self, elems: list):
        for elem in elems:
            if isinstance(elem, list):
                kwargs = dict(zip(["by", "elem"], elem))
                self.safeclick(**kwargs)
                continue
            self.safeclick(elem)
        return True

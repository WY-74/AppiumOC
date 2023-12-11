import time
from appium.webdriver.common.appiumby import AppiumBy


class AppiumOC:
    def __init__(self, driver) -> None:
        self.driver = driver

    def _sleep(self, times: int = 1):
        time.sleep(times)

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
        if not self.attribute(elem, "clickable"):
            raise Exception("clickable = False")
        elem.click()
        return True

    def multi_click(self, elems: list):
        for elem in elems:
            if isinstance(elem, list):
                kwargs = dict(zip(["by", "elem"], elem))
                self.safeclick(**kwargs)
                continue
            self.safeclick(elem)
        return True

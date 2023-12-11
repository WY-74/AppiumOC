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

from selenium.common.exceptions import NoSuchElementException


def remove_pop_ups(func):
    def wapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except NoSuchElementException as e:
            for black in self.blacklist:
                _elems = self.driver.find_elements(*black)
                if _elems:
                    _elems[0].click()
                    return func(*args, **kwargs)
            raise e

    return wapper

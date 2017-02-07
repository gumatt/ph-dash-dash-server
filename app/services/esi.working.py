from page_objects import PageObject, PageElement
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

MANAGE_ORG_BTN_XPATH = '//*[@id="header-user"]/a[3]'
CALL_HISTORY_BTN_XPATH = '//*[@id="nav-callhistory"]/a'
DATE_FILTER_BTN_XPATH = '//*[@id="content"]/div[6]/div[1]/a[1]'
FILTER_FOOTER_XPATH = './/*[@id="callhistoryFiltersForm"]/div[3]'
RECORD_COUNT_XPATH = '//*[@id="content"]/div[7]/div[2]/div[3]'


def get_selenium_driver(browser='Chrome'):
    if browser == 'Chrome':
        return webdriver.Chrome('/Users/gumatt/Dropbox/proj/libs/chromedriver')
    else:
        return webdriver.PhantomJS()

class LoginPage(PageObject):
    username = PageElement(id_='LoginUsername')
    password = PageElement(id_='LoginPassword')
    login_btn = PageElement(id_='loginBtn')
    manage_org_btn = PageElement(xpath=MANAGE_ORG_BTN_XPATH)
    scope_badge = PageElement(id_='scopeButton')

    def login(self, username, password):
        self.username = username
        self.password = password
        self.login_btn.click()

class PortalHomePage(PageObject):
    manage_org_btn = PageElement(xpath=MANAGE_ORG_BTN_XPATH)

class ManagerHomePage(PageObject):
    call_hist_btn = PageElement(xpath=CALL_HISTORY_BTN_XPATH)

class CallHistoryPage(PageObject):
    date_filter_btn = PageElement(xpath=DATE_FILTER_BTN_XPATH)
    date_filter_form = PageElement(id_='callhistoryFiltersForm')

    @property
    def is_visible(self):
        return 'Call History' in self.w.title

    @property
    def current_record_count(self):
        if not self.is_visible:
            return '0'
        
        rec_count = WebDriverWait(self.w, 10).until(EC.element_to_be_clickable((By.XPATH, RECORD_COUNT_XPATH)))
        return rec_count.text

    # @property
    # def filter_input_visible(self):
    #     return self.date_filter_form.is_displayed()

    # @property
    # def from_input(self):
    #     wait = WebDriverWait(self.w, 10)
    #     from_input = wait.until(EC.element_to_be_clickable((By.ID, 'from-0')))
    #     return PageElement(id_='from-0')

    # @property
    # def to_input(self):
    #     wait = WebDriverWait(self.w, 10)
    #     from_input = wait.until(EC.element_to_be_clickable((By.ID, 'to-0')))
    #     return PageElement(id_='to-0')

    # @property
    # def set_filters_btn(self):
    #     filter_footer = PageElement(xpath=FILTER_FOOTER_XPATH)
    #     set_filters = PageElement(css='input[type="submit"]', context=True)
    #     return set_filters(filter_footer)

    @property
    def current_date_filters(self):
        filters = WebDriverWait(self.w, 10).until(
            EC.element_to_be_clickable((By.ID, 'filter_date'))
        )
        return filters.text

    def set_filters(self, from_date='', to_date=''):
        self.date_filter_btn.click()
        from_date_input = WebDriverWait(self.w, 10).until(
            EC.element_to_be_clickable((By.ID, 'from-0')))
        from_date_input.send_keys(from_date)
        to_date_input = WebDriverWait(self.w, 10).until(EC.element_to_be_clickable((By.ID, 'to-0')))
        to_date_input.send_keys(to_date)
        set_filter_button = self.w.find_element_by_xpath(FILTER_FOOTER_XPATH).find_element_by_tag_name("input")
        set_filter_button.click()
        WebDriverWait(self.w, 2)



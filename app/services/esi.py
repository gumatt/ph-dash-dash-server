__author__ = 'gumatt'

import re
import logging
from datetime import timedelta, datetime, date
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger('ph_dashboard_logger')
logger.setLevel(logging.INFO)


# Phone record fields
CALLERID = 0
CALLERNUM = 1
DIALEDNUM = 2
ANSWERNUM = 4
DATETIME = 5
DURATION = 6

CALL_HISTORY_TITLE = "Call History"
MIN_CALL_DURATION = timedelta(seconds=13)
NO_LINK_URL = 'no link'
DEFAULT_REC_COUNT_PER_PAGE = 25
DOWNLOAD_LINK_CLASS = "cdraudio"


def clean_ESI_date(date_string):
    """
    clean the uffix letters from the ESI date string

    >>> clean_ESI_date("Apr 22nd, 4:37pm")
    'Apr 22, 4:37pm'
    >>> clean_ESI_date("Today, 08:11am")
    'Today, 08:11am'
    >>> clean_ESI_date("Yesterday, 4:53pm")
    'Yesterday, 4:53pm'
    """
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_string)


def origintime_to_datetime(otime=""):
    """

    :param otime: string of format ("Today, 5:20pm", "Jun 19th, 7:43pm",
    :return:
    """
    today = datetime.today()
    if "Today" in otime:
        datestr = today.strftime("%b %d %Y")
        ctime = otime.replace("Today", datestr)
    elif "Yesterday" in otime:
        cdate = today - timedelta(days=1)
        datestr = cdate.strftime("%b %d %Y")
        ctime = otime.replace("Yesterday", datestr)
    elif (date.today().year - 1).__str__() in otime:
        ctime = otime
    else:
        ctime = otime.replace(',', ' {},'.format(date.today().year.__str__()))

    ctime = clean_ESI_date(ctime)

    # ctime = today.strftime("%Y") + ' ' + ctime

    logging.debug("ctime=  %s" % ctime)
    odt = datetime.strptime(ctime, '%b %d %Y, %I:%M%p')

    if (today.month == 1) & (odt.month == 12):
        odt = odt.replace(year=today.year - 1)

    return odt


def string_to_duration(duration_text="00:00"):
    mins_secs = duration_text.split(":")
    # logger.debug('mins_secs = %s' % mins_secs)
    mins = int(mins_secs[0])
    secs = int(mins_secs[1])
    # logger.debug('mins = %s, and secs = %s' % (mins, secs))
    hrs = int(mins / 60)
    mins -= hrs * 60
    # logger.debug('hrs = %s, and mins = %s' % (hrs, mins))
    dur = timedelta(hours=hrs, minutes=mins, seconds=secs)
    # logger.debug("final duration is %s" % dur)
    return dur


def download_file(url, to_filename):
    local_filename = to_filename
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return local_filename


def get_rec_counts_from_string(count_string):
    p = re.compile('\d+')
    nums = p.findall(count_string.strip())
    return nums


def get_current_record_count(count_string):
    nums = get_rec_counts_from_string(count_string)
    if len(nums) > 0:
        return int(nums[0])
    else:
        return 0


def get_record_count(count_string):
    nums = get_rec_counts_from_string(count_string)
    if len(nums) > 1:
        return int(nums[1])
    elif len(nums) == 1:
        return int(nums[0])
    else:
        return 0


class ESICallRecord(object):
    def __init__(self, caller_id="", calling_num="",
                 dialed_num="", answer_num="", timestamp=datetime.now(),
                 duration=timedelta(seconds=0), file_url=""):
        self.caller_id = caller_id
        self.caller_num = calling_num
        self.dialed_num = dialed_num
        self.answer_num = answer_num
        self.timestamp = timestamp
        self.duration = duration
        self.file_url = file_url

    def __str__(self):
        my_str = 'Caller ID:    %s \n' % self.caller_id
        my_str += 'Calling Num:   %s \n' % self.caller_num
        my_str += 'Dialed Num:   %s \n' % self.dialed_num
        my_str += 'Answered Num: %s \n' % self.answer_num
        my_str += 'Timestamp:    %s \n' % self.timestamp
        my_str += 'Duration:     %s \n' % self.duration
        my_str += 'Filename:     %s \n' % self.file_url
        return my_str

    def archive_directory(self):
        return self.timestamp.strftime("%Y/%Y-%m %B")

    def archive_filename(self):
        filename = self.timestamp.strftime("%Y.%m.%d %I.%M%p ")
        filename = filename + " " + self.caller_num + " to " + self.answer_num + ".wav"
        return filename

    def full_pathname(self, base_url="/Users/gumatt/Box Sync/Corp Docs (internal access only)/phone backups"):
        return base_url + "/" + self.archive_directory() + "/" + self.archive_filename()

    def to_json(self):
        data = {
            'from_name': self.caller_id,
            'caller_phone': self.caller_num,
            'dialed_phone': self.dialed_num,
            'answer_phone': self.answer_num,
            'timestamp': self.timestamp.strftime('%b %d %Y, %I:%M%p'),
            'duration': self.duration.seconds,
            'audio_file': self.file_url
        }
        return data

class ESIScraper(object):
    xpaths = {'usernameTxtBox': ".//*[@id='LoginUsername']",
              'passwordTxtBox': ".//*[@id='LoginPassword']",
              'submitButton': ".//*[@id='login-submit']/div/input",
              'mgrButton': ".//*[@id='header-user']/a[3]",
              'callHistoryButton': ".//*[@id='nav-callhistory']/a",
              'show100Button': ".//*[@id='content']/div[7]/div[2]/div[2]/ul/li[5]/a",
              'show50Button': ".//*[@id='content']/div[7]/div[2]/div[2]/ul/li[4]/a",
              'show25Button': ".//*[@id='content']/div[7]/div[2]/div[2]/ul/li[3]/a",
              # 'show15Button': ".//*[@id='content']/div[8]/div[2]/div[2]/ul/li[2]/a",
              'show15Button': ".//*[@id='content']/div[7]/div[2]/div[2]/ul/li[2]/a",
              'lastof100download': ".//*[@id='content']/div[8]/div[1]/table/tbody/tr[180]/td[7]/a[1]",
              'calltable': ".//*[@id='content']/div[7]/div[1]/table/tbody",
              'filterFooter': ".//*[@id='callhistoryFiltersForm']/div[3]",
              'dateFilterButton': ".//*[@id='content']/div[6]/div[1]/a[1]",
              'fromDateField': ".//*[@id='from-0']",
              'toDateField': ".//*[@id='to-0']",
              'setFiltersButton': ".//*[@id='submit-209846327']",
              'recordcount': ".//*[@id='content']/div[7]/div[2]/div[3]"
              }

    def __init__(self, url="https://my.esihs.net/portal/", username="105@powerhousetl.com", password=""):
        self.url = url
        self.username = username
        self.password = password
        self.mydriver = webdriver.Chrome('/Users/gumatt/Dropbox/proj/libs/chromedriver')
        # self.mydriver = webdriver.PhantomJS()

    def _navigate_to_call_history(self):
        try:
            if self.on_call_history_page():
                return
            
            self.mydriver.get(self.url)

            # Clear Username TextBox if already allowed "Remember Me"
            self.mydriver.find_element_by_id('LoginUsername').clear()

            # Write Username in Username TextBox
            self.mydriver.find_element_by_id('LoginUsername').send_keys(self.username)

            # Clear Password TextBox if already allowed "Remember Me"
            self.mydriver.find_element_by_xpath(self.xpaths['passwordTxtBox']).clear()

            # Write Password in password TextBox
            self.mydriver.find_element_by_xpath(self.xpaths['passwordTxtBox']).send_keys(self.password)

            # Click Login button
            self.mydriver.find_element_by_xpath(self.xpaths['submitButton']).click()
 
            self.mydriver.find_element_by_xpath(self.xpaths['mgrButton']).click()
            logger.debug("mgrButton clicked -- navigating to Manager Portal")

            # logger.debug("waiting for Call History button")
            # mgr_button = WebDriverWait(self.mydriver, 20).until(EC.presence_of_element_located((By.XPATH, "callHistoryButton")))
            logger.debug("clicking Call History button")
            # mgr_button.click()
            self.mydriver.find_element_by_xpath(self.xpaths['callHistoryButton']).click()
            # logger.debug("Call History button clicked")

        # except TimeoutException:
        #     logger.debug("catching TimeoutException")
        #     self.mydriver.execute_script("window.stop()")
        except Exception, e:
            logger.exception(e)
            self.mydriver.quit()
            raise e

    @staticmethod
    def _get_file_link_from_element(element):
        """

        :type element: WebElement retrieved by selenium
        """
        link = NO_LINK_URL
        if "action-buttons" in element.get_attribute('class'):
            link_node = element.find_element_by_tag_name("a")
            if 'download-audio' in link_node.get_attribute('class'):
                link = link_node.get_attribute('href')
            logger.info("link is %s" % link)
        else:
            logger.debug('_get_file_link_from_element:  element text is %s' % element.text)
        return link

    def _get_file_link_for_data_term_id(self, audio_id):
        selector = "audio-{}".format(audio_id)
        logger.debug("selector = {}".format(selector))
        file_link_elements = self.mydriver.find_elements_by_id(selector)
        logger.debug('{} elements found for {}'.format(len(file_link_elements), selector))
        if file_link_elements:
            audio_elements = file_link_elements[0].find_elements_by_tag_name('source')
            logger.debug("{} audio source link found for {}".format(len(audio_elements), audio_id))
            link = audio_elements[0].get_attribute('src')
            logger.debug("file link = {}".format(link))
            return link
        else:
            return NO_LINK_URL

    def _read_call_table_to_data(self, table):
        call_list = []
        call_rows = table.find_elements_by_tag_name('tr')
        logger.debug('{} rows read in call_table'.format(len(call_rows)))
        for r in call_rows:
            if r.get_attribute('data-term-id') is None:
                continue
            logger.debug('_read_call_table_to_data:  reading row %s' % r.text)
            call_els = r.find_elements_by_tag_name("td")
            # file_link = self._get_file_link_from_element(call_els[FILELINK])
            call_id = r.get_attribute('data-orig-id')
            file_link = self._get_file_link_for_data_term_id(call_id)
            call_list.append(ESICallRecord(call_els[CALLERID].text,
                                           calling_num=call_els[CALLERNUM].text,
                                           dialed_num=call_els[DIALEDNUM].text,
                                           answer_num=call_els[ANSWERNUM].text,
                                           timestamp=origintime_to_datetime(call_els[DATETIME].text),
                                           duration=string_to_duration(call_els[DURATION].text),
                                           file_url=file_link))
        # logger.debug("_read_call_table_to_datat:  call_list is /n %s" % [str(item) for item in call_list])
        logger.info('_read_call_table_to_data:  call_list has %s elements' % len(call_list))
        return call_list

    def _set_date_filters(self, fromdate='06/01/2015', todate='06/30/2015'):
        if not self.on_call_history_page():
            self._navigate_to_call_history()

        logger.info("clicking filters button...")
        self.mydriver.find_element_by_xpath(self.xpaths['dateFilterButton']).click()

        logger.info("waiting for filters dialog to appear...")
        wait = WebDriverWait(self.mydriver, 15)
        wait.until(EC.element_to_be_clickable((By.ID, 'from-0')))
        logger.info("filters dialog now visible.  Setting date filter from %s to %s..." % (fromdate, todate))
        self.mydriver.find_element_by_xpath(self.xpaths['fromDateField']).clear()
        self.mydriver.find_element_by_xpath(self.xpaths['fromDateField']).send_keys(fromdate)

        self.mydriver.find_element_by_xpath(self.xpaths['toDateField']).clear()
        self.mydriver.find_element_by_xpath(self.xpaths['toDateField']).send_keys(todate)

        logger.debug("date fields filters filled in setting filters...")
        self.mydriver.find_element_by_xpath(self.xpaths['filterFooter']).find_element_by_tag_name("input").click()
        rec_count = self.get_current_record_count_on_page()
        logger.debug("%s records on the resulting page..." % rec_count)
        return rec_count

    @staticmethod
    def get_duration_from_call_row(row):
        logger.debug("get_duration_from_call_row:  raw data is %s" % row.text)
        els = row.find_elements_by_tag_name('td')
        logger.debug("get_duration_from_call_row:  els count is %s" % len(els))
        if len(els) >= DURATION:
            duration_text = els[DURATION].text
            logger.debug("get_duration_from_call_row:  raw duration is %s" % duration_text)
        else:
            duration_text = "0:00"
        return string_to_duration(duration_text)

    def get_current_record_count_on_page(self):
        logger.debug('entering get_current_record_count_on_page...')
        if not self.on_call_history_page():
            return 0

        wait = WebDriverWait(self.mydriver, 15)
        wait.until(EC.element_to_be_clickable((By.XPATH, self.xpaths['recordcount'])))
        rec_count_text = self.mydriver.find_element_by_xpath(self.xpaths['recordcount']).text

        return get_current_record_count(rec_count_text)

    def get_total_record_count(self):
        if not self.on_call_history_page():
            return 0

        wait = WebDriverWait(self.mydriver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, self.xpaths['recordcount'])))
        # rec_count_el = WebDriverWait(self.mydriver, 3).until(EC.visibility_of(self.mydriver.find_element_by_xpath(self.xpaths['recordcount'])))

        # rec_count_text = rec_count_el.text
        rec_count_text = self.mydriver.find_element_by_xpath(self.xpaths['recordcount']).text
        logger.debug("record count text is [%s]" % rec_count_text)

        return get_record_count(rec_count_text)

    def on_call_history_page(self):
        #logger.debug("looking for page title")
        #logger.debug("self.mydriver = %s" % self.mydriver)
        #logger.debug("self.mydriver.title exists: %s" % hasattr(self.mydriver, 'title'))
        #logger.debug("the title is : [%s]" % self.mydriver.title)
        return CALL_HISTORY_TITLE in self.mydriver.title

    def next_page(self):
        if not self.on_call_history_page():
            return 0

        next_button = self.mydriver.find_element_by_link_text('>')
        next_button_class = next_button.get_attribute('class')
        # logger.debug("next button class(es): %s" % next_button_class)
        if (next_button_class == "") | ('disabled' in next_button.get_attribute('class')):
            return 0

        next_button.click()
        return self.get_current_record_count_on_page()

    def set_page_size(self, count=50):
        logger.debug("entering set_page_size w count=%s" % count)
        if not self.on_call_history_page():
            logger.info("Not on call history page")
            return -1

        if count not in [15, 25, 50, 100]:
            logger.info("record count %s not valid" % count)
            return -1

        button_path_name = "show" + str(count) + "Button"
        logger.debug("buttons path name is %s" % button_path_name)
        wait = WebDriverWait(self.mydriver, 10)
        count_button = wait.until(EC.presence_of_element_located((By.XPATH, self.xpaths[button_path_name])))
        logger.debug("element found is '{}'".format(count_button.text)) 
        self.mydriver.get(count_button.get_attribute("href"))
        # count_button.click()
        # self.mydriver.find_element_by_xpath(self.xpaths[button_path_name]).click()
        logger.debug("do you see me?")
        logger.debug("page title is [%s]" % self.mydriver.title)
        return self.get_current_record_count_on_page()

    def read_call_history_data(self):
        logger.debug("entering read_call_history_data")
        calls = []
        if not self.on_call_history_page():
            logger.info("not on Call History page...")
            return calls

        rec_count = curr_count = self.get_current_record_count_on_page()
        while rec_count > 0:
            self.wait_for_links_to_load(45)
            tot_count = self.get_total_record_count()
            call_table = self.mydriver.find_element_by_xpath(self.xpaths['calltable'])
            calls.extend(self._read_call_table_to_data(call_table))
            logger.info("read %s of %s records" % (curr_count, tot_count))
            rec_count = self.next_page()
            curr_count += rec_count
        return calls

    def call_history_data(self, fromdate="06/15/2015", todate="06/15/2015", page_size=DEFAULT_REC_COUNT_PER_PAGE):
        try:
            if not self.on_call_history_page():
                logger.info("calling _navigate_to_call_history...")
                self._navigate_to_call_history()
            logger.info("calling _set_date_filters from %s to %s" % (fromdate, todate))
            self._set_date_filters(fromdate, todate)
            logger.info("calling set_page_size...")
            self.set_page_size(page_size)
            logger.info("calling read_call_history_data...")
        except Exception, e:
            self.mydriver.quit()
            raise e

        return self.read_call_history_data()

    def call_count(self, fromdate="06/15/2015", todate="06/15/2015"):
        try:
            if not self.on_call_history_page():
                self._navigate_to_call_history()
            self._set_date_filters(fromdate, todate)
        except Exception, e:
            self.mydriver.quit()
            raise e

        return self.get_total_record_count()

    def wait_for_links_to_load(self, seconds=45):


        if not self.on_call_history_page():
            logger.info("calling _navigate_to_call_history...")
            self._navigate_to_call_history()

        start = datetime.now()
        now = datetime.now()
        link_count = new_link_count = 0
        last_link_count_timestamp = datetime.now()
        # logger.debug("runtime: %s  :: time_since_last_new_link: %s" % (now-start, now-last_link_count_timestamp))
        while ((now - start) <= timedelta(seconds=seconds)) & (
                    (now - last_link_count_timestamp) < timedelta(seconds=15)):
            links = self.mydriver.find_elements_by_class_name(DOWNLOAD_LINK_CLASS)
            new_link_count = len(links)
            # logger.debug("current link_count is %s at %s" % (new_link_count, datetime.now()))
            now = datetime.now()
            if new_link_count > link_count:
                link_count = new_link_count
                last_link_count_timestamp = now
        logger.debug("current link_count is %s at %s" % (new_link_count, datetime.now()))
        logger.debug("runtime: %s  :: time_since_last_new_link: %s" % (now - start, (now - last_link_count_timestamp)))

    def quit(self):
        self.mydriver.quit()

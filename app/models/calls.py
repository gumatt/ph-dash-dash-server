import re
from datetime import timedelta, datetime, date
from mongoengine import Document, StringField, DateTimeField, IntField, URLField
from mongoengine.queryset.visitor import Q

PHONE_NUM_SEG_SEPARATOR = '-'
EXTERNAL_NUM_PREFIX = '1'
PARKED_CALL_PREFIX = 'Call Parked at '

ESI_DATE_FORMAT = '%b %d %Y'

ERROR_MSG_BAD_SECONDS = 'bad duration string: seconds too large'

class CallDuration(object):
    @classmethod
    def sanitize(cls, duration):
        if isinstance(duration, int):
            return duration
        elif isinstance(duration, str):
            minutes = duration.strip().split(':')[0]
            seconds = duration.strip().split(':')[1]
            if int(seconds) > 59:
                raise ValueError(ERROR_MSG_BAD_SECONDS)
            return timedelta(minutes=int(minutes), seconds=int(seconds)).total_seconds()


class PhoneNumber(object):
    _number = ''

    def __init__(self, the_number):
        self.phone_number = the_number

    @classmethod
    def standardize(cls, the_number):
        '''
        takes a string phone number and attempts to standardize it in
        the format:  1-XXX-XXX-XXXX

        Assumes all numbers are US domestic, or internal extensions of the
        form 1XX
        '''
        if the_number.startswith(PARKED_CALL_PREFIX):
            the_number = the_number.lstrip(PARKED_CALL_PREFIX)
        formatted = re.sub('[()]', '', the_number.strip().replace(' ', '-'))
        if formatted.startswith(EXTERNAL_NUM_PREFIX):
            return formatted
        else:
            return '1-' + formatted

    @property
    def phone_number(self):
        return self._number

    @phone_number.setter
    def phone_number(self, the_number):
        self._number = PhoneNumber.standardize(the_number)


class CallTimeStamp(object):
    @classmethod
    def strip_today_ts(cls, time_stamp):
        today_str = datetime.today().strftime(ESI_DATE_FORMAT)
        return time_stamp.replace('Today', today_str)

    @classmethod
    def strip_yesterday_ts(cls, time_stamp):
        yesterday_date = datetime.today() - timedelta(days=1)
        yesterday_str = yesterday_date.strftime(ESI_DATE_FORMAT)
        return time_stamp.replace('Yesterday', yesterday_str)

    @classmethod
    def standardize(cls, time_stamp_str):
        '''
        Take ESI Date field string and standardize to a timestamp
        '''
        if isinstance(time_stamp_str, datetime):
            return time_stamp_str
        time_stamp_str = time_stamp_str.strip()
        if time_stamp_str.startswith('Today'):
            time_stamp_str = CallTimeStamp.strip_today_ts(time_stamp_str)
        elif time_stamp_str.startswith('Yesterday'):
            time_stamp_str = CallTimeStamp.strip_yesterday_ts(time_stamp_str)
        elif (date.today().year - 1).__str__() in time_stamp_str:
            # time stamp is from last year and has a year string in iter
            pass
        else:
            # time stamp does not have a year and current year needs to be inserted
            time_stamp_str = time_stamp_str.replace(',', ' {},'.format(date.today().year.__str__()))
        time_stamp_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', time_stamp_str)
        datetime_ts = datetime.strptime(time_stamp_str, '%b %d %Y, %I:%M%p')
        return datetime_ts


class Call(Document):
    from_name = StringField() # "From" field from ESI
    caller_phone = StringField() # "Caller ID" field form ESI
    dialed_phone = StringField() # "Dialed" field from ESI - number the caller dialed
    answer_phone = StringField() # "Receivied By" field from ESI
    timestamp = DateTimeField()
    duration = IntField()
    #    audio = URLField() # if file was saved on the Box, link to the audio file

    def __init__(self, **kwargs):
        Document.__init__(self, **kwargs)
        self.caller_phone = PhoneNumber.standardize(kwargs.get('caller_phone'))
        self.dialed_phone = PhoneNumber.standardize(kwargs.get('dialed_phone'))
        self.answer_phone = PhoneNumber.standardize(kwargs.get('answer_phone'))
        self.timestamp = CallTimeStamp.standardize(kwargs.get('timestamp'))
        self.duration = CallDuration.sanitize(kwargs.get('duration'))


def agent_calls(name, duration_limit='10'):
    return Call.objects(
        Q(from_name__icontains=name) |
        Q(answer_phone__icontains=name) &
        Q(duration__gte=duration_limit)
        ).to_json()





























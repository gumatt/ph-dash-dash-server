import unittest
from freezegun import freeze_time
import datetime
from app.models import calls
from app.models.calls import Call

POWERHOUSE_MAIN_NUMBER = '(202) 333-5380'
PARKED_CALL_ON_10 = 'Call Parked at 10'
ANSWERED_INTERNALLY_CALL = 'Davina Proffitt (104)'

TODAY_CALL_TS = 'Today, 4:37pm'
YESTERDAY_CALL_TS = 'Yesterday, 11:52am'

ST_CALL_TS = '	Feb 1st, 11:49am'
XST_CALL_TS = '	Jan 31st, 3:37pm'
ND_CALL_TS = 'Feb 2nd, 4:12pm'
RD_CALL_TS = 'Jan 3rd, 10:37am'
NTH_CALL_TS = 'Jan 30th, 11:55am'
LAST_BUSDAY_TS = 'Dec 29th 2016, 07:35am'
FIRST_BUSDAY_TS = 'Jan 2nd, 09:46am'

TODAY_STR = '2017-02-04'
NEW_YEARS_DAY_STR = '2017-01-01'
FIRST_BUS_DAY = '2017-01-03'

ZERO_DURATION = '0:00'
SUB_HOUR_DURATION = '12:34'
HOUR_PLUS_DURATION = '153:12'
BAD_SECONDS_DURATION = '123:67'



class PhoneNumberTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_scrub_origin_phone_number(self):
        self.assertEqual('1-202-333-5380', calls.PhoneNumber.standardize(POWERHOUSE_MAIN_NUMBER))

    def test_scub_outside_number(self):
        self.assertEqual('1-610-373-7999', calls.PhoneNumber.standardize('1 (610) 373-7999'))

    def test_scrub_exetension(self):
        self.assertEqual('101', calls.PhoneNumber.standardize('101'))

    def test_parked_call(self):
        self.assertEqual('10', calls.PhoneNumber.standardize(PARKED_CALL_ON_10))

    def test_answered_internally_call(self):
        self.assertEqual(
            '1-Davina-Proffitt-104',
            calls.PhoneNumber.standardize(ANSWERED_INTERNALLY_CALL)
        )

class CallTimeStampTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @freeze_time(TODAY_STR)
    def test_cleanup_today_timestamp(self):
        self.assertEqual(
            'Feb 04 2017, 4:37pm',
            calls.CallTimeStamp.strip_today_ts(TODAY_CALL_TS))


    @freeze_time(TODAY_STR)
    def test_standardize_today_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 02, 04, 16, 37),
            calls.CallTimeStamp.standardize(TODAY_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_yesterday_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 02, 03, 11, 52),
            calls.CallTimeStamp.standardize(YESTERDAY_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_a_first_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 02, 01, 11, 49),
            calls.CallTimeStamp.standardize(ST_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_an_st_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 01, 31, 15, 37),
            calls.CallTimeStamp.standardize(XST_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_an_nd_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 02, 02, 16, 12),
            calls.CallTimeStamp.standardize(ND_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_an_rd_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 01, 03, 10, 37),
            calls.CallTimeStamp.standardize(RD_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_an_nth_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 01, 30, 11, 55),
            calls.CallTimeStamp.standardize(NTH_CALL_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_prior_year_ts(self):
        self.assertEqual(
            datetime.datetime(2016, 12, 29, 7, 35),
            calls.CallTimeStamp.standardize(LAST_BUSDAY_TS)
        )

    @freeze_time(TODAY_STR)
    def test_standardize_curr_year_ts(self):
        self.assertEqual(
            datetime.datetime(2017, 01, 02, 9, 46),
            calls.CallTimeStamp.standardize(FIRST_BUSDAY_TS)
        )


class CallDurationTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_zero_duration(self):
        self.assertEqual(
            0,
            calls.CallDuration.sanitize(ZERO_DURATION)
        )

    def test_sub_hour_duration(self):
        self.assertEqual(
            754,
            calls.CallDuration.sanitize(SUB_HOUR_DURATION)
        )

    def test_hour_plus_duration(self):
        self.assertEqual(
            9192,
            calls.CallDuration.sanitize(HOUR_PLUS_DURATION)
        )

    def test_bad_seconds_duration(self):
        with self.assertRaises(ValueError) as context:
            calls.CallDuration.sanitize(BAD_SECONDS_DURATION)

        self.assertTrue(calls.ERROR_MSG_BAD_SECONDS in context.exception)

    def test_int_duration_under_60(self):
        self.assertEqual(
            47,
            calls.CallDuration.sanitize(47)
        )
        self.assertEqual(
            calls.CallDuration.sanitize('0:47'),
            calls.CallDuration.sanitize(47)
        )

    def test_int_duration_over_60(self):
        self.assertEqual(
            9192,
            calls.CallDuration.sanitize(9192)
        )
        self.assertEqual(
            calls.CallDuration.sanitize(HOUR_PLUS_DURATION),
            calls.CallDuration.sanitize(9192)
        )

class CallDataTests(unittest.TestCase):
    def setUp(self):
        self.call = Call(
            from_name='Elaine Levin',
            caller_phone='(202) 333-5380',
            dialed_phone='1 (208) 799-2000',
            answer_phone='1 (208) 799-2000',
            timestamp='Dec 29th 2016, 2:48pm',
            duration='7:08')

    def tearDown(self):
        Call.drop_collection()

    def test_call_object_exists(self):
        self.assertIsInstance(self.call, Call)

    def test_call_can_be_saved(self):
        self.call.save()

    def test_call_properties(self):
        self.assertEqual('Elaine Levin', self.call.from_name)
        self.assertEqual(428, self.call.duration)
        self.assertEqual('1-202-333-5380', self.call.caller_phone)
        self.assertEqual('1-208-799-2000', self.call.dialed_phone)
        self.assertEqual('1-208-799-2000', self.call.answer_phone)

    @freeze_time(TODAY_STR)
    def test_call_timestamp(self):
        self.assertEqual(
            datetime.datetime(2016, 12, 29, 14, 48),
            self.call.timestamp
        )

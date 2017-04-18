import os
import logging
from flask_script import Manager, Server


from app import create_app
from app.services.esi import ESIScraper
from app.models import Call

logger = logging.getLogger('ph_dashboard_logger')
handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:  %(asctime)s -- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

manager.add_command('runserver', Server(host='0.0.0.0', port=9000))

@manager.command
@manager.option('--from_date', '-f', dest='from_date', help='from date')
@manager.option('--to_date', '-t', dest='to_date', help='to date')
@manager.option('--size', '-s', dest='size', help='page size')
def db_update(from_date, to_date, size=50):
    esi = ESIScraper(password='7585')
    logger.info("scraper created...")
    esi._set_date_filters(fromdate=from_date, todate=to_date)
    count = esi.get_total_record_count()
    logger.info(
        'loading {} call(s) to the database'.format(count))
    esi.set_page_size(count=size)
    data = esi.read_call_history_data()
    esi.quit()
    if len(data) > 0:
        for d in data:
            call = Call(
                from_name=d.caller_id,
                caller_phone=d.caller_num,
                dialed_phone=d.dialed_num,
                answer_phone=d.answer_num,
                timestamp=d.timestamp,
                duration=d.duration.seconds
            )
            call.save()

# @manager.command
# def runserver():
#     app.

# @manager.command
# def test_watch():
#     server = LiveReloadServer()
#     server.watch('./test/results/*.html')
#     server.serve(root='test/results')

# @manager.command
# def test():
#     # import green
#     # green.cmdline.sys.argv = ['', '-vvv']
#     # green.main()
#     report_filename = './test/results/testresults.html'
#     fp = file(report_filename, 'wb')
#     runner = HTMLTestRunner(
#         stream=fp,
#         title='My unit test',
#         description='This demonstrates the report output by HTMLTestRunner.'
#     )

#     # Use an external stylesheet.
#     # See the Template_mixin class for more customizable options
#     runner.STYLESHEETS = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" type="text/css">'
#     # runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" type="text/css">'
#     tests = unittest.TestLoader().discover('.', pattern='test_*.py')
#     # run the test
#     # tester = TestProgram(testRunner=runner)
#     # tester.runTests()
#     # print report_file
#     runner.run(tests)
#     print 'done'
#     # runner.run(my_test_suite)

if __name__ == '__main__':
    manager.run()

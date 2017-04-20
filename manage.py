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
        'loading %s call(s) to the database', count)
    esi.set_page_size(count=size)
    data = esi.read_call_history_data()
    esi.quit()
    if len(data) > 0:
        for item in data:
            call = Call(
                from_name=item.caller_id,
                caller_phone=item.caller_num,
                dialed_phone=item.dialed_num,
                answer_phone=item.answer_num,
                timestamp=item.timestamp,
                duration=item.duration.seconds
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

if __name__ == '__main__':
    manager.run()

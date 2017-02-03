import os
# import unittest
from app import create_app
from flask_script import Manager, Server
# from test.HTMLTestRunner import TestProgram, HTMLTestRunner
# from livereload import Server as LiveReloadServer

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

manager.add_command('runserver', Server(host='0.0.0.0', port=9000))

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

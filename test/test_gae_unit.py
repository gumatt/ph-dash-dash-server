from nose.plugins.attrib import attr
from nose.tools import assert_true

@attr('gae')
@attr('unit')
def test_testing():
    assert_true(True)

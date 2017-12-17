from nose.tools import assert_equals

"""
ALL tests must be named starting with 'test_'
For example, this file should not be tested
Rename this file to 'test_simple.py' for nose to detect this file

"""

def test_true():
    assert_equals(1, 1, 'This should SUCCEED')

def test_false():
    assert_equals(1, 0, 'This should FAIL')

def test_ok():
    ok_(True, 'shorthand for assert')
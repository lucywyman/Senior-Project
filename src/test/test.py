#!/usr/bin/env python3
from py_test_osu import test_suite
import dummy

test = test_suite()

test.describe('Basic tests',4)
test.assert_equals(1,1,'one equals one')
test.assert_not_equals(1,2,'one does not equal two')
test.expect(1==1,'a true statement')
test.assert_equals('hello',dummy.dummyfunc(),'testing works?')
test.conclude()

var test_suite = require('./js_test_osu');
var dummy = require('./dummy');


var test = new test_suite();

test.describe('Basic tests',10);

test.assert_equals(1,1,'one equals one');
test.assert_not_equals(1,2,'one does not equal two');
test.expect(1===1,'a true statement');
test.expect_error("generated error?", dummy, "module.err()");
test.assert_equals('hello',dummy.dummy(),'testing works?');

test.assert_equals(1,2,'one equals two');
test.assert_not_equals(1,1,'one does not equal one');
test.expect(1!==1,'a false statement');
test.expect_error("no generated error?", dummy, "module.dummy()");
test.assert_equals('hello',dummy.notdummy(),"testing fails?");

test.conclude();
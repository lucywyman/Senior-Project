<?php

include "php_test_osu.php";
include "dummy.php";


$test = new test_suite($argv[1], $argv[2], $argv[3]);

$test->describe("Basic tests", 10);

$test->assert_equals(1, 1, "one equals one");
$test->assert_not_equals(1, 2, "one does not equal two");
$test->expect(1===1, "a true statement");
$test->expect_error("generated error?", "err();");
$test->assert_equals("hello", dummy(), "testing works?");

$test->assert_equals(1, 2, "one equals two");
$test->assert_not_equals(1, 1,"one does not equal one");
$test->expect(1!==1, "a false statement");
$test->expect_error("no generated error?", "dummy();");
$test->assert_equals("hello", notdummy(), "testing fails?");

$test->conclude();

?>
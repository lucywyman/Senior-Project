#include "cpp_test_osu.hpp"
#include "dummy.hpp"
#include <string>

int main(int argc, char* argv[]){
  
    // args 0-2: submission_ID, test_ID and output directory
    test_suite test (std::stoi(argv[1]), std::stoi(argv[2]), argv[3]);
    
    test.describe("Basic tests",12);

    test.assert_equals(1, 1, "one equals one");
    test.assert_not_equals(1, 2, "one does not equal two");
    test.assert_equals('a', 'a', "'a' equals 'a'");
    test.assert_not_equals('a', 'b', "'a' does not equal 'b'");
    test.expect(1==1, "a true statement");
    test.assert_equals(std::string("hello"), dummy(), "testing works?");

    test.assert_equals(1,2,"one equals two");
    test.assert_not_equals(1,1,"one does not equal one");
    test.assert_equals('a', 'b', "'a' equals 'b'");
    test.assert_not_equals('a', 'a', "'a' does not equal 'a'");
    test.expect(1!=1,"a false statement");
    test.assert_equals(std::string("hello"), notdummy(), "testing fails?");

    test.conclude();
    
    return 0;
}
#ifndef C_TEST_OSU_H_
#define C_TEST_OSU_H_

typedef struct _testStats{
  int testCount;
  int testsRemain;
  float weightTotal;
  float weightAcc;
  //These form the return object
  char* TAPstring;
  char* Tests;
  char* Errors;
  int Grade;
  int sub_ID;
  int test_ID;
} _testStats;

_testStats* tester_init(char* argv[]);

void ok(char* message, float weight, _testStats* t);
void notok(char* message, float weight, _testStats* t);

void _logj(char* ok, int testNumber, char* message, float weight, _testStats* t);

void tester_conclude(_testStats* t);

void assert_equals(void* actual, void* expected, int bytes, char* message, float weight, _testStats* t);
void assert_not_equals(void* actual, void* expected, int bytes, char* message, float weight, _testStats* t);
void expect(int passed, char* message, float weight, _testStats* t);

void tester_describe(char* message, int tests, _testStats* t);
void tester_it(char* message, _testStats* t);

#endif //C_TEST_OSU_H_
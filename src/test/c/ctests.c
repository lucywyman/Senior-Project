#include "c_test_osu.h"
#include "student.h"

int main(int argc, char* argv[]){
  
  int av = 0;
  int ev = 0;
  int *avp = &av;
  int *evp = &ev;
  char test_str[] = "hello";
  char *str_ptr = &test_str[0];
  
  _testStats *t = tester_init(argv);
  
  tester_describe("Basic tests",4,t);
  
  av = 1;
  ev = 1;
  assert_equals(avp, evp, sizeof(1), "one equals one", 1, t);
  
  ev = 2;
  assert_not_equals(avp, evp, sizeof(2), "one does not equal two", 1, t);
  
  expect(1==1, "a true statement", 1, t);
  
  assert_equals(dummyfunc(), str_ptr, sizeof(test_str)-1, "testing works?", 1, t);
  
  tester_conclude(t);
  return 0;
}
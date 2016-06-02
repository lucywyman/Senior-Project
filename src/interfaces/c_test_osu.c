#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "c_test_osu.h"
#define BUF_L 16384


_testStats* tester_init(char* argv[]){
  _testStats* t = malloc(sizeof(_testStats));
  t->testCount = 0;
  t->testsRemain = 0;
  t->weightTotal = 0;
  t->weightAcc = 0;
  t->TAPstring = malloc(sizeof(char)*BUF_L);
  strcpy(t->TAPstring,"\"TAP\": \"");
  t->Tests = malloc(sizeof(char)*BUF_L);
  strcpy(t->Tests,"\"Tests\": [");
  t->Errors = malloc(sizeof(char)*BUF_L);
  strcpy(t->Errors,"\"Errors\": [");
  t->sub_ID = atoi(argv[1]);
  t->test_ID = atoi(argv[2]);
  t->output = malloc(sizeof(char)*256);
  strcpy(t->output,argv[3]);
  return t;
}

void _logj(char* ok, int testNumber, char* message, float weight, _testStats* t){
  char buf[16];
  t->Tests = strcat(t->Tests,"{\"state\":\"");
  t->Tests = strcat(t->Tests,ok);
  t->Tests = strcat(t->Tests,"\",\"testNumber\":\"");
  snprintf(buf,16,"%d",testNumber);
  t->Tests = strcat(t->Tests,buf);
  t->Tests = strcat(t->Tests,"\",\"message\":\"");
  t->Tests = strcat(t->Tests,message);
  t->Tests = strcat(t->Tests,"\",\"weight\":\"");
  snprintf(buf,16,"%f",weight);
  t->Tests = strcat(t->Tests,buf);
  t->Tests = strcat(t->Tests,"\"},");
  t->TAPstring = strcat(t->TAPstring,ok);
  t->TAPstring = strcat(t->TAPstring," ");
  snprintf(buf,16,"%d",testNumber);
  t->TAPstring = strcat(t->TAPstring,buf);
  t->TAPstring = strcat(t->TAPstring," ");
  t->TAPstring = strcat(t->TAPstring,message);
  t->TAPstring = strcat(t->TAPstring," ");
  snprintf(buf,16,"%f",weight);
  t->TAPstring = strcat(t->TAPstring,buf);
  t->TAPstring = strcat(t->TAPstring,"\\n");
}

void ok(char* message, float weight, _testStats* t){
  t->testCount++;
  t->testsRemain--;
  if(t->testsRemain < 0){
    printf("# Exceeded declared test count for this \"describe\"!\n");
    t->Errors = strcat(t->Errors,"Exceeded declared test count for a describe.,");
  }
  _logj("ok",t->testCount,message,weight,t);
}

void notok(char* message, float weight, _testStats* t){
  t->testCount++;
  t->testsRemain--;
  if(t->testsRemain < 0){
    printf("# Exceeded declared test count for this \"describe\"!");
    t->Errors = strcat(t->Errors,"Exceeded declared test count for a describe.,");
  }
  _logj("not ok ",t->testCount,message,weight,t);
}

void tester_conclude(_testStats* t){
  char buf[256];
  if(t->testsRemain > 0){
    printf("# More tests declared than executed!\n");
    t->Errors = strcat(t->Errors,"More tests declared than executed.,");
  }
  if(t->Tests[strlen(t->Tests)-1]==',') t->Tests[strlen(t->Tests)-1] = ']';
  else{
    t->Tests = strcat(t->Tests,"]");
  }
  if(t->Tests[strlen(t->Errors)-1]==',') t->Tests[strlen(t->Errors)-1] = ']';
  else{
    t->Errors = strcat(t->Errors,"]");
  }
  snprintf(buf,256,"%s/%d",t->output,t->test_ID);
  FILE* out = fopen(buf,"w");
  fputs("{",out);
  fputs(t->TAPstring,out);
  fputs("\", ",out);
  fputs(t->Tests,out);
  fputs(", ",out);
  fputs(t->Errors,out);
  fputs(", \"Grade\": ",out);
  if(t->weightTotal==0) t->weightTotal = 1;
  snprintf(buf,256,"%f",t->weightAcc/t->weightTotal);
  fputs(buf,out);
  fputs("}",out);
  fclose(out);
}

//Testing Functions
void assert_equals(void* actual, void* expected, int bytes, char* message, float weight, _testStats* t){
  t->weightTotal += weight;
  if(!memcmp(actual,expected,bytes)){
    ok(message,weight,t);
    t->weightAcc += weight;
  }
  else{
    notok(message,weight,t);
  }
}

void assert_not_equals(void* actual, void* expected, int bytes, char* message, float weight, _testStats* t){
  t->weightTotal += weight;
  if(memcmp(actual,expected,bytes)){
    ok(message,weight,t);
    t->weightAcc += weight;
  }
  else{
    notok(message,weight,t);
  }
}

//No thunks for C.

//if passed is not zero, passes
void expect(int passed, char* message, float weight, _testStats* t){
  t->weightTotal += weight;
  if(passed){
    ok(message,weight,t);
    t->weightAcc += weight;
  }
  else{
    notok(message,weight,t);
  }
}

//Grouping Functions
void tester_describe(char* message, int tests, _testStats* t){
  char buf[16];
  snprintf(buf,16,"%d",t->testCount+1);
  strcat(t->TAPstring,buf);
  t->TAPstring = strcat(t->TAPstring,"..");
  snprintf(buf,16,"%d",t->testCount+tests);
  t->TAPstring = strcat(t->TAPstring,buf);
  t->TAPstring = strcat(t->TAPstring,"# ");
  t->TAPstring = strcat(t->TAPstring,message);
  t->TAPstring = strcat(t->TAPstring,"\\n");
  t->testsRemain = tests;
}

// what does this function do? where is it called?
void tester_it(char* message, _testStats* t){
  t->TAPstring = strcat(t->TAPstring,"# ");
  t->TAPstring = strcat(t->TAPstring,message);
}
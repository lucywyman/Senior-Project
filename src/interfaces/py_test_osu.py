import operator
import json
import sys
import os

class test_suite:
    def __init__(self):
        # note: when this line was farther down, it was erasing
        # record of attributes above it
        self.__dict__ = {}

        self.testCount = 0
        self.testsRemain = 0
        self.TAPstring = ''
        self.weightTotal = 0
        self.weightAcc = 0
        self.jsonRet = json.loads('{"TAP":"","Tests":[],"Errors":[],"Grade":""}')

        self.sub_ID = sys.argv[1]
        self.test_ID = sys.argv[2]
        self.output = sys.argv[3]

    #Helper functions
    def ok(self,message,weight):
        self.testCount += 1
        self.testsRemain -= 1
        self.weightAcc += weight
        if(self.testsRemain < 0):
            print('# Exceeded declared test count for this "describe"!')
            self.jsonRet['Errors'].append("Exceeded declared test count for a describe.")
        self.logj('ok',self.testCount,message,weight)
    def notok(self,message,weight):
        self.testCount += 1
        self.testsRemain -= 1
        if(self.testsRemain < 0):
            print('# Exceeded declared test count for this "describe"!')
            self.jsonRet['Errors'].append("Exceeded declared test count for a describe.")
        self.logj('not ok',self.testCount,message,weight)

    def logj(self,ok,testNumber,message,weight):
      testj = json.loads('{"state":"'+ok+'","testNumber":'+str(testNumber)+',"message":"'+message+'","weight":'+str(weight)+'}')
      self.jsonRet['Tests'].append(testj)
      self.TAPstring += ' '.join([ok,str(testNumber),message,str(weight)]) + '\n'

    def conclude(self):
      if(self.testsRemain > 0):
          print('# More tests declared than executed!')
          self.jsonRet['Errors'].append("More tests declared than executed.")
      self.jsonRet['TAP'] = self.TAPstring
      self.jsonRet['Grade'] = self.weightAcc/self.weightTotal
      resfile = open(os.path.normpath(os.path.join(self.output,str(self.test_ID))),'w')
      json.dump(self.jsonRet,resfile)

    #Testing functions
    def assert_equals(self,actual,expected,message,weight=1):
        self.weightTotal += weight
        if(operator.eq(actual,expected)):
            self.ok(message,weight)
        else:
            self.notok(message,weight)

    def assert_not_equals(self,actual,unexpected,message,weight=1):
        self.weightTotal += weight
        if(operator.ne(actual,unexpected)):
            self.ok(message,weight)
        else:
            self.notok(message,weight)

    def expect_error(self,message,thunk,weight=1):
        self.weightTotal += weight
        try:
            thunk()
            self.notok(message,weight)
        except:
            self.ok(message,weight)

    def expect(self,passed,message,weight=1):
        self.weightTotal += weight
        if(passed):
            self.ok(message,weight)
        else:
            self.notok(message,weight)

    #Grouping functions
    def describe(self,message,tests):
        self.TAPstring += str(self.testCount + 1) + '..' + str(self.testCount + tests)
        self.TAPstring += '# ' + message + '\n'
        self.testsRemain = tests

    def it(self,message):
        self.TAPstring += '# ' + message

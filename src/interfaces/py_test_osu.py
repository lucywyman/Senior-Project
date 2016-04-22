import operator
import json
import sys

class test_suite:
    def __init__(self):
        self.testCount = 0
        self.testsRemain = 0
        self.TAPstring = ''
        self.weightTotal = 0
        self.weightAcc = 0
        self.jsonRet = json.loads('{"TAP":"","Tests":[],"Errors":[],"Grade":""}')
        self.__dict__ = {}
        self._connectVars = ''
        self.testID = 0
        self._connectVars = sys.argv[1]
        self.sub_ID = sys.argv[2]
        self.test_ID = sys.argv[3]
        sys.argv[1] = "You shouldn't be looking at this."
        sys.argv[2] = 0
        sys.argv[3] = 0
        
    #Helper functions
    def ok(self,message,weight):
        self.testCount += 1
        self.testsRemain -= 1
        if(self.testsRemain < 0): 
            print('# Exceeded declared test count for this "describe"!')
            self.jsonRet['Errors'].append("Exceeded declared test count for a describe.")
        logj('ok ',self.testCount,message,weight)
    def notok(self,message,weight):
        self.testCount += 1
        self.testsRemain -= 1
        if(self.testsRemain < 0): 
            print('# Exceeded declared test count for this "describe"!')
            self.jsonRet['Errors'].append("Exceeded declared test count for a describe.")
        logj('not ok',self.testCount,message,weight)
    
    def logj(self,ok,testNumber,message,weight):
      testj = json.loads('{"state":'+ok+',"testNumber":'+str(testNumber)+',"message":'+message+',"weight":'+str(weight)+'}')
      self.jsonRet['Tests'].append(testj)
      self.TAPstring += ' '.join([ok,str(testNumber),message,str(weight)]) + '\n'
    
    def conclude(self)
      if(self.testsRemain > 0): 
          print('# More tests declared than executed!')
          self.jsonRet['Errors'].append("More tests declared than executed.")
      self.jsonRet['TAP'] = self.TAPstring
      self.jsonRet['Grade'] = self.weightAcc/self.weightTotal
      conn = psycopg2.connect(self._connectVars, cursor_factory= psycopg2.extras.RealDictCursor)
      conn.autocommit = True
      cur = conn.cursor()
      cur.execute("""
                        INSERT INTO submissions_have_results (submission_id, test_id, results)
                        VALUES (%s, %s, %s)
                        """, (self.sub_ID, self.test_ID, json.dumps(self.jsonRet))
                        )
      cur.close()
      
    #Testing functions
    def assert_equals(self,actual,expected,message,weight=0):
        self.weightTotal += weight
        if(operator.eq(actual,expected)):
            self.ok(message,weight)
            self.weightAcc += weight
        else:
            self.notok(message,weight)
            
    def assert_not_equals(self,actual,unexpected,message,weight=0):
        self.weightTotal += weight
        if(operator.ne(actual,unexpected)):
            self.ok(message,weight)
            self.weightAcc += weight
        else:
            self.notok(message,weight)
            
    def expect_error(self,message,thunk,weight=0):
        self.weightTotal += weight
        try:
            thunk()
            self.notok(message,weight)
        except:
            self.ok(message,weight)
            self.weightAcc += weight
            
    def expect(self,passed,message,weight=0):
        self.weightTotal += weight
        if(passed):
            self.ok(message,weight)
            self.weightAcc += weight
        else:
            self.notok(message,weight)
            
    #Grouping functions
    def describe(self,message,tests):
        self.TAPstring += str(self.testCount + 1) + '..' + str(self.testCount + tests))
        self.TAPstring += '# ' + message
        self.testsRemain = tests
    def it(self,message):
        self.TAPstring += '# ' + message

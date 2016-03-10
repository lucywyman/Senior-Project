import operator

class test_suite:
    def __init__(self):
        self.testcount = 0
        self.testsremain = 0
        
    #Helper functions
    def ok(self,message):
        self.testcount += 1
        self.testsremain -= 1
        if(self.testsremain < 0): print('# Exceeded declared test count for this "describe"!')
        print('ok ' + str(self.testcount) + ' ' + message)
    def notok(self,message):
        self.testcount += 1
        self.testsremain -= 1
        if(self.testsremain < 0): print('# Exceeded declared test count for this "describe"!')
        print('not ok ' + str(self.testcount) + ' ' + message)
        
    #Testing functions
    def assert_equals(self,actual,expected,message):
        if(operator.eq(actual,expected)):
            self.ok(message)
        else:
            self.notok(message)
    def assert_not_equals(self,actual,unexpected,message):
        if(operator.ne(actual,unexpected)):
            self.ok(message)
        else:
            self.notok(message)
    def expect_error(self,message,thunk):
        try:
            thunk()
            self.notok(message)
        except:
            self.ok(message)
    def expect(self,passed,message):
        if(passed):
            self.ok(message)
        else:
            self.notok(message)
            
    #Grouping functions
    def describe(self,message,tests):
        print(str(self.testcount + 1) + '..' + str(self.testcount + tests))
        print('# ' + message)
        self.testsremain = tests
    def it(self,message):
        print('# ' + message)

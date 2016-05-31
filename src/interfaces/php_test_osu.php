<?php
class test_suite {

        private $testCount = 0;
        private $testsRemain = 0;
        private $TAPstring = '';
        private $weightTotal = 0;
        private $weightAcc = 0;
        private $jsonRet = json_decode("{\"TAP\":\"\",\"Tests\":[],\"Errors\":[],\"Grade\":\"\"}");

        private $sub_ID = sys.argv[1];
        private $test_ID = sys.argv[2];
        private $output = sys.argv[3];

    #Helper functions
    public function ok(message,weight) {
        $this->testCount += 1;
        $this->testsRemain -= 1;
        if($this->testsRemain < 0) {
            print("# Exceeded declared test count for this \"describe\"!");
            $this->jsonRet["Errors"].append("Exceeded declared test count for a describe.");
        }
        $this->logj('ok ',$this->testCount,message,weight);
    }
    
    public function notok(message, weight) {
        $this->testCount += 1;
        $this->testsRemain -= 1;
        if($this->testsRemain < 0) {
            print("# Exceeded declared test count for this \"describe\"!");
            $this->jsonRet["Errors"].append("Exceeded declared test count for a describe.");
        }
        $this->logj('not ok', $this->testCount, message, weight);
    }

    public function logj(self,ok,testNumber,message,weight) {
      $testj = json_decode("{\"state\":\""+ok+"\",\"testNumber\":\""+str(testNumber)+"\",\"message\":\""+message+"\",\"weight\":"+str(weight)+"}");
      $this->jsonRet["Tests"].append($testj);
      $this->TAPstring += " ".join([ok,str(testNumber),message,str(weight)]) + "\n";
    }

    public function conclude(self) {
      if($this->testsRemain > 0) {
          print("# More tests declared than executed!");
          $this->jsonRet["Errors"].append("More tests declared than executed.");
      }
      $this->jsonRet["TAP"] = $this->TAPstring;
      $this->jsonRet["Grade"] = $this->weightAcc/$this->weightTotal;
      $resfile = fopen(os.path.normpath(os.path.join($this->output,str($this->test_ID))),"w");
      $jResult = json_encode($this->jsonRet);
      fwrite($resfile, $jResult);
      fclose($resfile);
    }

    #Testing functions
    public function assert_equals(self,actual,expected,message,weight=1) {
        $this->weightTotal += weight;
        if(operator.eq(actual,expected)) {
            $this->ok(message,weight);
            $this->weightAcc += weight;
        }
        else {
            $this->notok(message,weight);
        }
    }

    public function assert_not_equals(self,actual,unexpected,message,weight=1) {
        $this->weightTotal += weight;
        if(operator.ne(actual,unexpected)) {
            $this->ok(message,weight);
            $this->weightAcc += weight;
        }
        else {
            $this->notok(message,weight);
        }
    }

    public function expect_error(self,message,thunk,weight=1) {
        $this->weightTotal += weight;
        try {
            thunk()
            $this->notok(message,weight);
        }
        catch {
            $this->ok(message,weight);
            $this->weightAcc += weight;
        }
    }

    public function expect(self,passed,message,weight=1) {
        $this->weightTotal += weight;
        if(passed) {
            $this->ok(message,weight);
            $this->weightAcc += weight;
        }
        else {
            $this->notok(message,weight);
        }
    }

    #Grouping functions
    public function describe(self,message,tests) {
        $this->TAPstring += str($this->testCount + 1) + ".." + str($this->testCount + tests);
        $this->TAPstring += "# " + message + "\n";
        $this->testsRemain = tests;
    }
    
    public function it(self,message) {
        $this->TAPstring += "# " + message;
    }
}
?>
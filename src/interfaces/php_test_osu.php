<?php
class test_suite {

    private $testCount = 0;
    private $testsRemain = 0;
    private $TAPstring = '';
    private $weightTotal = 0;
    private $weightAcc = 0;
    private $jsonRet = "";

    private $sub_ID = 0;
    private $test_ID = 0;
    private $output = "";

    function __construct($sid, $tid, $oPath) {

        $this->jsonRet  = json_decode("{\"TAP\":\"\",\"Tests\":[],\"Errors\":[],\"Grade\":\"\"}");
        $this->sub_ID   = $sid;
        $this->test_ID  = $tid;
        $this->output   = $oPath;
    }


    #Helper functions
    public function ok($message, $weight) {
        $this->testCount    += 1;
        $this->testsRemain  -= 1;
        $this->weightAcc    += $weight;

        if ($this->testsRemain < 0) {
            echo "# Exceeded declared test count for this \"describe\"!" . PHP_EOL;
            $this->jsonRet->Errors[] = "Exceeded declared test count for a describe.";
        }

        $this->logj("ok", $this->testCount, $message, $weight);
    }

    public function notok($message, $weight) {
        $this->testCount    += 1;
        $this->testsRemain  -= 1;

        if($this->testsRemain < 0) {
            echo "# Exceeded declared test count for this \"describe\"!" . PHP_EOL;
            $this->jsonRet->Errors[] = "Exceeded declared test count for a describe.";
        }

        $this->logj("not ok", $this->testCount, $message, $weight);
    }

    public function logj($ok, $testNumber, $message, $weight) {
        $testj = json_decode("{\"state\":\"" . $ok . "\",\"testNumber\":\"" . (string)$testNumber . "\",\"message\":\"" . $message . "\",\"weight\":" . (string)$weight . "}");
        $this->jsonRet->Tests[] = $testj;
        $this->TAPstring .= join(" ", array($ok, (string)$testNumber, $message, (string)$weight)) . "\n";
    }

    public function conclude() {
        if($this->testsRemain > 0) {
            echo "# More tests declared than executed!";
            $this->jsonRet->Errors[] = "More tests declared than executed.";
        }

        $this->jsonRet->TAP   = $this->TAPstring;
        $this->jsonRet->Grade = $this->weightAcc/$this->weightTotal;

        $fpath = $this->path_join($this->output, (string)$this->test_ID);

        $resfile = fopen($fpath, "w");
        $jResult = json_encode($this->jsonRet);

        fwrite($resfile, $jResult);
        fclose($resfile);
    }

    #Testing functions
    public function assert_equals($actual, $expected, $message, $weight=1, $type="exact") {
        $this->weightTotal  += $weight;

        if($type == "exact") {
            if($actual === $expected){
                $this->ok($message, $weight);
            } else {
                $this->notok($message, $weight);
            }
        } else {
            if ($actual == $expected) {
                $this->ok($message, $weight);
            } else {
                $this->notok($message, $weight);
            }
        }
    }

    public function assert_not_equals($actual, $expected, $message, $weight=1, $type="exact") {
        $this->weightTotal  += $weight;

        if($type == "exact") {
            if($actual !== $expected) {
                $this->ok($message, $weight);
            } else {
                $this->notok($message, $weight);
            }
        } else {
            if ($actual != $expected) {
                $this->ok($message, $weight);
            } else {
                $this->notok($message, $weight);
            }
        }
    }

    public function expect_error($message, $thunk, $weight=1) {
        $this->weightTotal  += $weight;
        try {
            eval($thunk);
            $this->notok($message, $weight);
        } catch (Exception $e) {
            $this->ok($message, $weight);
        }
    }

    public function expect($passed, $message, $weight=1) {
        $this->weightTotal  += $weight;

        if ($passed) {
            $this->ok($message, $weight);
        }
        else {
            $this->notok($message, $weight);
        }
    }

    #Grouping functions
    public function describe($message, $tests) {
        $this->TAPstring    .= (string)($this->testCount + 1) . ".." . (string)($this->testCount + $tests);
        $this->TAPstring    .= "# " . $message . "\n";
        $this->testsRemain   = $tests;
    }

    public function it($message) {
        $this->TAPstring    .= "# " . $message;
    }

    private function path_join() {
        $path = array();

        foreach (func_get_args() as $arg) {
            if ($arg !== "") {
                $path[] = $arg;
            }
        }

        return preg_replace("#/+#", "/", join("/", $path));
    }
}
?>
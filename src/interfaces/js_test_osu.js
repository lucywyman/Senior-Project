var test_suite = function (){
  this.testCount = 0;
  this.testsRemain = 0;
  this.TAPstring = '';
  this.weightTotal = 0;
  this.weightAcc = 0;
  this.jsonRet = JSON.parse('{"TAP":"","Tests":[],"Errors":[],"Grade":""}');
  this.sub_ID = process.argv[2]
  this.test_ID = process.argv[3]
  this.output = process.argv[4]
}

test_suite.prototype.ok = function(message,weight){
  this.testCount++;
  this.testsRemain--;
  this.weightAcc += weight;
  if(this.testsRemain<0){
    console.log('# Exceeded declared test count for this "describe"!');
    this.jsonRet['Errors'].push("Exceeded declared test count for a describe.");
  }
  this.logj('ok',this.testCount,message,weight);
}

test_suite.prototype.notok = function(message,weight){
  this.testCount++;
  this.testsRemain--;
  if(this.testsRemain<0){
    console.log('# Exceeded declared test count for this "describe"!');
    this.jsonRet['Errors'].push("Exceeded declared test count for a describe.");
  }
  this.logj('not ok',this.testCount,message,weight);
}

test_suite.prototype.logj = function(ok,testNumber,message,weight){
  testj = JSON.parse('{"state":"'+ok+'","testNumber":'+testNumber+',"message":"'+message+'","weight":'+weight+'}');
  this.jsonRet['Tests'].push(testj);
  this.TAPstring += [ok,testNumber,message,weight].join(' ') + '\n';
}

test_suite.prototype.conclude = function() {
  if(this.testsRemain > 0){
    console.log('# More tests declared than executed!');
    this.jsonRet['Errors'].push("More tests declared than executed.");
  }
  this.jsonRet['TAP'] = this.TAPstring;
  this.jsonRet['Grade'] = this.weightAcc/this.weightTotal;
  //write out
  var fs = require('fs');
  var path = require("path");
  var outFile = path.join(this.output, this.test_ID.toString());
  fs.writeFile(outFile,JSON.stringify(this.jsonRet))
}
//testing functions
test_suite.prototype.assert_equals = function(actual,expected,message,weight,type){
  weight = weight || 1;
  type = type || 'exact';
  this.weighTotal += weight;
  if(type=='exact'){
    if(actual===expected){
      this.ok(message,weight);
    }
    else{
      this.notok(message,weight);
    }
  }
  else{
    if(actual==expected){
      this.ok(message,weight);
    }
    else{
      this.notok(message,weight);
    }
  }
}

test_suite.prototype.assert_not_equals = function(actual,expected,message,weight,type){
  weight = weight || 1;
  type = type || 'exact';
  this.weighTotal += weight;
  if(type=='exact'){
    if(actual!==expected){
      this.ok(message,weight);
    }
    else{
      this.notok(message,weight);
    }
  }
  else{
    if(actual!=expected){
      this.ok(message,weight);
    }
    else{
      this.notok(message,weight);
    }
  }
}

//expects the thunk you'd like evaluated as a string
test_suite.prototype.expect_error = function(message, module, thunk, weight){
  weight = weight || 1;
  this.weighTotal += weight;
  try{
    eval(thunk);
    this.notok(message,weight);
  }
  catch(err){
    this.ok(message,weight);
  }
}

test_suite.prototype.expect = function(passed,message,weight){
  weight = weight || 1;
  this.weighTotal += weight;
  if(passed){
    this.ok(message,weight);
  }
  else{
    this.notok(message,weight);
  }
}

test_suite.prototype.describe = function(message,tests){
  this.TAPstring += (this.testCount + 1) + '..' + (this.testCount + tests);
  this.TAPstring += '# ' + message + '\n';
  this.testsRemain = tests;
}

test_suite.prototype.it = function(message){
  this.TAPstring += '# ' + message;
}

module.exports = test_suite;
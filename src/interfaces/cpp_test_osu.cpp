#include <json/value.h>
#include <json/json.h>
#include <json/reader.h>
#include <json/writer.h>

#include <string>
#include <iostream>
#include <fstream>

#include <boost/algorithm/string/join.hpp>
#include <vector>

#include "cpp_test_osu.hpp"

#include <sstream>
namespace patch
{
    template < typename T > std::string to_string( const T& n )
    {
        std::ostringstream stm ;
        stm << n ;
        return stm.str() ;
    }

    int stoi(const std::string& s) {
        std::istringstream str(s);
        int i;
        str >> i;
        return i;
    }
}


test_suite::test_suite(const std::string sID, const std::string tID, const std::string op) {

    testCount = 0;
    testsRemain = 0;
    TAPstring = "";
    weightTotal = 0;
    weightAcc = 0;

    sub_ID     = patch::stoi(sID);
    test_ID    = patch::stoi(tID);
    output     = op;
    parser.parse("{\"TAP\":\"\",\"Tests\":[],\"Errors\":[],\"Grade\":\"\"}", jsonRet);
}

void test_suite::ok(const std::string message, int weight) {
    testCount++;
    testsRemain--;
    weightAcc += weight;
    if (testsRemain < 0) {
        std::cout << "# Exceeded declared test count for this \"describe\"!" << std::endl;
        jsonRet["Errors"].append("Exceeded declared test count for a describe.");
    }
    logj("ok", testCount, message, weight);
}

void test_suite::notok(const std::string message, int weight) {
    testCount++;
    testsRemain--;
    if(testsRemain<0){
        std::cout << "# Exceeded declared test count for this \"describe\"!" << std::endl;
        jsonRet["Errors"].append("Exceeded declared test count for a describe.");
    }
    logj("not ok", testCount, message, weight);
}

void test_suite::logj(std::string ok, int testNumber, const std::string message, int weight){
    Json::Value testj;
    std::string toParse = "{\"state\":\"" + ok + "\",\"testNumber\":" + patch::to_string(testNumber) + ",\"message\":\"" + message + "\",\"weight\":" + patch::to_string(weight) + "}";

    parser.parse(toParse, testj);
    jsonRet["Tests"].append(testj);

    std::vector<std::string> list;
    list.push_back(ok);
    list.push_back(patch::to_string(testNumber));
    list.push_back(message);
    list.push_back(patch::to_string(weight));

    TAPstring += boost::algorithm::join(list, " ") + "\n";
}

void test_suite::conclude(void) {
    if(testsRemain > 0){
        std::cout << "# More tests declared than executed!";
        jsonRet["Errors"].append("More tests declared than executed.");
    }

    int grade = weightAcc/weightTotal;

    jsonRet["TAP"] = TAPstring;
    jsonRet["Grade"] = grade;

    //write out
    std::string outputFile = path_join(output, patch::to_string(test_ID));

    std::ofstream fs;
    fs.open(outputFile, std::fstream::out);

    fs << writer.write(jsonRet);
    fs.close();
}

//testing functions
void test_suite::expect(bool passed, const std::string message, int weight) {
    weightTotal += weight;

    if (passed){
        ok(message, weight);
    }
    else {
        notok(message, weight);
    }
}


void test_suite::describe(const std::string message, int tests) {
    TAPstring += patch::to_string(testCount + 1) + ".." + patch::to_string(testCount + tests);
    TAPstring += "# " + message + "\n";
    testsRemain = tests;
}


void test_suite::it(const std::string message) {
  TAPstring += "# " + message;
}

std::string test_suite::path_join(std::string dir, std::string file) {

    std::string temp = dir;
    std::string result;

    if (dir[dir.length()] != '/') {
        temp += '/';
    }

    result = temp + file;
    return result;
}

#ifndef CPP_TEST_OSU_HPP_
#define CPP_TEST_OSU_HPP_
#include <string>
#include <json/json.h>

class test_suite
{

    public:
        test_suite(const std::string sID, const std::string tID, const std::string op);
        void ok(const std::string message, int weight);
        void notok(const std::string message, int weight);
        void logj(std::string ok, int testNumber, const std::string message, int weight);
        void conclude(void);
        template<typename T>
        void assert_equals(T actual, T expected, const std::string message, int weight = 1);
        template<typename T>
        void assert_not_equals(T actual, T expected, const std::string message, int weight = 1);
        void expect(bool passed, const std::string message, int weight = 1);
        void describe(const std::string message, int tests);
        void it(const std::string message);


    private:
        Json::Value jsonRet;
        Json::Reader parser;
        Json::StyledWriter writer;
        int testCount;
        int testsRemain;
        std::string TAPstring;
        int weightTotal;
        int weightAcc;
        int sub_ID;
        int test_ID;
        std::string output;
        std::string path_join(std::string dir, std::string file);
};

// Templated functions must have implementation in header
// so that compiler can generate code for instances of template
template<typename T>
void test_suite::assert_equals(T actual, T expected, const std::string message, int weight) {
    weightTotal += weight;

    if (actual == expected) {
        ok(message, weight);
    }
    else {
        notok(message, weight);
    }
}


template<typename T>
void test_suite::assert_not_equals(T actual, T expected, const std::string message, int weight) {
    weightTotal += weight;

    if (actual != expected) {
        ok(message, weight);
    }
    else {
        notok(message, weight);
    }
}

#endif //CPP_TEST_OSU_HPP_
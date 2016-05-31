package edu.oregonstate.test.java;

import org.json.simple.JSONObject;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import org.json.simple.parser.JSONParser;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.StringJoiner;

import java.io.FileWriter;
import java.io.IOException;

import java.nio.file.Path;
import java.nio.file.Paths;



public class java_test_osu{

    private JSONParser parser = new JSONParser();
    private Object jsonRet = null;
    private int testCount = 0;
    private int testsRemain = 0;
    private String TAPstring = "";
    private int weightTotal = 0;
    private int weightAcc = 0;
    private ArrayList<String> errors = new ArrayList<String>();
    private ArrayList<JSONObject> tests = new ArrayList<JSONObject>();
    private int sub_ID = 0;
    private int test_ID = 0;
    private String output = "";


    public java_test_osu(int sID, int tID, String op) {
        this.sub_ID     = sID;
        this.test_ID    = tID;
        this.output     = op;
        try {
            this.jsonRet = parser.parse("{\"TAP\":\"\",\"Tests\":[],\"Errors\":[],\"Grade\":\"\"}");
        } catch(org.json.simple.parser.ParseException err) {
            System.out.print(err.getMessage());
        }
    }

    public void ok(String message, int weight){
        this.testCount++;
        this.testsRemain--;
        this.weightAcc += weight;
        if(this.testsRemain<0){
            System.out.print("# Exceeded declared test count for this \"describe\"!");
            this.errors.add("Exceeded declared test count for a describe.");
        }
        this.logj("ok",this.testCount,message, weight);
    }

    public void notok(String message, int weight) {
        this.testCount++;
        this.testsRemain--;
        if(this.testsRemain<0){
            System.out.print("# Exceeded declared test count for this \"describe\"!");
            this.errors.add("Exceeded declared test count for a describe.");
        }
        this.logj("not ok",this.testCount,message, weight);
    }

    public void logj(String ok, int testNumber, String message, int weight){
        Object testj = null;
        try {
            testj = this.parser.parse("{\"state\":\""+ok+"\",\"testNumber\":"+testNumber+",\"message\":\""+message+"\",\"weight\":"+weight+"}");
        }
        catch(org.json.simple.parser.ParseException err) {
            System.out.print(err.getMessage());
        }
        this.tests.add((JSONObject) testj);

        StringJoiner joiner = new StringJoiner(" ");
        joiner.add(ok).add(String.valueOf(testNumber)).add(message).add(String.valueOf(weight));
        this.TAPstring += joiner.toString() + "\n";
    }

    @SuppressWarnings("unchecked")
    public void conclude() {
        if(this.testsRemain > 0){
            System.out.print("# More tests declared than executed!");
            this.errors.add("More tests declared than executed.");
        }

        JSONObject jRet = (JSONObject)this.jsonRet;
        int grade = this.weightAcc/this.weightTotal;

        jRet.put("TAP", this.TAPstring);
        jRet.put("Grade", String.valueOf(grade));
        jRet.put("Tests", this.tests);

        //write out
        Path outputFile = Paths.get(this.output, String.valueOf(this.test_ID));

        try (FileWriter file = new FileWriter(outputFile.normalize().toString())) {
            file.write(jRet.toJSONString());
        } catch (IOException e) {
            System.out.println(e);
        }
    }

    //testing functions
    public void assert_equals(Object actual, Object expected, String message, int weight) {
        this.weightTotal += weight;

        if (actual.equals(expected)) {
            this.ok(message, weight);
        }
        else {
            this.notok(message, weight);
        }

    }
    // Set default weight
    public void assert_equals(Object actual, Object expected, String message) {
        this.assert_equals(actual, expected, message, 1);
    }

    public void assert_not_equals(Object actual, Object expected, String message, int weight) {
        this.weightTotal += weight;

        if (actual.equals(expected)) {
            this.notok(message, weight);
        }
        else {
            this.ok(message, weight);
        }
    }
    // Set default weight
    public void assert_not_equals(Object actual, Object expected, String message) {
        this.assert_not_equals(actual, expected, message, 1);
    }

    public void expect(boolean passed, String message, int weight) {
        this.weightTotal += weight;
        if(passed){
            this.ok(message, weight);
        }
        else{
            this.notok(message, weight);
        }
    }
    // Set default weight
    public void expect(boolean passed, String message) {
        this.expect(passed, message, 1);
    }

    public void describe(String message, int tests){
        this.TAPstring += (this.testCount + 1) + ".." + (this.testCount + tests);
        this.TAPstring += "# " + message + "\n";
        this.testsRemain = tests;
    }


    public void it(String message){
      this.TAPstring += "# " + message;
    }
}

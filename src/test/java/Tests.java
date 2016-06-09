package edu.oregonstate.classname.module;

import edu.oregonstate.test.java.java_test_osu;
import edu.oregonstate.classname.student.Dummy;

public class Tests{
    
    public static void main(String[] args) {
        
        // args 0-2: submission_ID, test_ID and output directory
        java_test_osu test = new java_test_osu(Integer.parseInt(args[0]), Integer.parseInt(args[1]), args[2]);
        
        test.describe("Basic tests",8);

        test.assert_equals(1,1,"one equals one");
        test.assert_not_equals(1,2,"one does not equal two");
        test.expect(1==1,"a true statement");
        test.assert_equals("hello",Dummy.dummy(),"testing works?");

        test.assert_equals(1,2,"one equals two");
        test.assert_not_equals(1,1,"one does not equal one");
        test.expect(1!=1,"a false statement");
        test.assert_equals("hello",Dummy.notdummy(),"testing fails?");

        test.conclude();
    }
}


JAVALIB = /usr/java/
MYPATH = $(CPATH):$(JAVALIB)

java_test_osu:
	javac -classpath $(MYPATH) -d . java_test_osu.java

student:
	javac -classpath $(MYPATH) -d . Dummy.java

runtest: java_test_osu student
	javac -classpath $(MYPATH) -d . Tests.java
	java -classpath $(MYPATH) edu.oregonstate.classname.module.Tests $(SUBID) $(TESTID) $(RESULTDIR)

runtest:
	g++ dummy.cpp cpp_test_osu.cpp tests.cpp -o tests -ljsoncpp -L$(CPATH) -std=c++11
	./tests $(SUBID) $(TESTID) $(RESULTDIR)
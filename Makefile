CXX      := g++
CXXFLAGS := -std=c++20 -O2 -Wall -Wextra -Wno-unused-parameter -g -Iinclude
LDFLAGS  :=

# Find all solution.cpp files
SRCS := $(wildcard */solution.cpp)
OBJS := $(SRCS:.cpp=.o)
BINS := $(SRCS:/solution.cpp=/solution)

.PHONY: all check clean list

# Default: compile-check all solutions (no linking, stubs have no main)
all: check

# Compile-check all solutions
check: $(OBJS)

# Compile-check a single problem: make check P=0001-two-sum
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Build a specific problem (requires main()): make build P=0001-two-sum
%/solution: %/solution.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

build: $(P)/solution

# Run a specific problem (requires main()): make run P=0001-two-sum
run: $(P)/solution
	./$(P)/solution

clean:
	rm -f $(OBJS) $(BINS)

# List all problem directories
list:
	@ls -d [0-9][0-9][0-9][0-9]-* 2>/dev/null | sort

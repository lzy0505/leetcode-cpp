// 6. Zigzag Conversion
// https://leetcode.com/problems/zigzag-conversion/
// Difficulty: Medium
// Tags: String
//
// The string "PAYPALISHIRING" is written in a zigzag pattern on a given number of rows like this: (you may want to display this pattern in a fixed font for better legibility)
//
// P   A   H   N
// A P L S I I G
// Y   I   R
//
// And then read line by line: "PAHNAPLSIIGYIR"
//
// Write the code that will take a string and make this conversion given a number of rows:
//
// string convert(string s, int numRows);
//
//
//
// Example 1:
//
// Input: s = "PAYPALISHIRING", numRows = 3
// Output: "PAHNAPLSIIGYIR"
//
// Example 2:
//
// Input: s = "PAYPALISHIRING", numRows = 4
// Output: "PINALSIGYAHRPI"
// Explanation:
// P     I    N
// A   L S  I G
// Y A   H R
// P     I
//
// Example 3:
//
// Input: s = "A", numRows = 1
// Output: "A"
//
//
//
// Constraints:
//
// 	  - 1 <= s.length <= 1000
//
// 	  - s consists of English letters (lower-case and upper-case), ',' and '.'.
//
// 	  - 1 <= numRows <= 1000

#include <stdio.h>
#include <string>
using namespace std;

class Solution {
public:
    string convert(string s, int numRows) {
        if (numRows <= 1) return s;

        string res ="";
        int T = 2 * numRows - 2;
        int C = s.size() / T + 1;

        for (int i = 0; i< numRows; i ++){
            if (i == 0 || i == numRows - 1){
                for (int c = 0; c < C; c ++)
                {
                    try { res += s.at(c * T + i); }
                    catch (...) { continue; }
                }
            } else {
                for (int c = 0; c < C; c ++)
                {
                    try { res += s.at(c * T + i); }
                    catch (...) { continue; }
                    try { res += s.at((c+1) * T - i); }
                    catch (...) { continue; }
                }
            }
        }

        return res;
    }
};

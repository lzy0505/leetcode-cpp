// 7. Reverse Integer
// https://leetcode.com/problems/reverse-integer/
// Difficulty: Medium
// Tags: Math
//
// Given a signed 32-bit integer x, return x with its digits reversed. If reversing x causes the value to go outside the signed 32-bit integer range [-2^31, 2^31 - 1], then return 0.
//
// Assume the environment does not allow you to store 64-bit integers (signed or unsigned).
//
//
//
// Example 1:
//
// Input: x = 123
// Output: 321
//
// Example 2:
//
// Input: x = -123
// Output: -321
//
// Example 3:
//
// Input: x = 120
// Output: 21
//
//
//
// Constraints:
//
// 	  - -2^31 <= x <= 2^31 - 1

#include <cstdint>
#include <stdio.h>
#include <vector>
using namespace std;

class Solution {
public:
    int reverse(int x) {
        unsigned int t = 0;
        int x0 = x;

        vector<int> digits, max, min;
        bool neg = (x < 0);

        while (x != 0)
        {
            digits.push_back(x % 10);
            x /= 10;
        }
        int len = digits.size();

        int int_max = INT32_MAX;

        while (int_max != 0)
        {
            max.push_back(int_max % 10);
            int_max /= 10;
        }

        int int_min = INT32_MIN;

        while (int_min != 0)
        {
            min.push_back(int_min % 10);
            int_min /= 10;
        }

        if (len <= 1) return x0;

        int res = 0;
        // whether the first digits (after reversing) are equal to the digits of the bound
        // this is the premise for checking overflow
        // false => no check, is safe
        // true => need check, may overflow
        // initial value is true only if the number of digits == that of the bound
        bool eq = ((neg && len == min.size()) || !neg && len == max.size());
        for (int i = 0; i < len; i++)
        {
            int j = len - 1 - i;
            // We check if overflow: only check when all the previous numbers are equal
            if (eq){
               // overflow
               if ((digits.at(i) > max.at(j) && !neg) || (digits.at(i) < min.at(j) && neg)) return 0;
               // update eq for the current number: the first smaller digit flip eq to false
               if ((digits.at(i) < max.at(j) && !neg) || (digits.at(i) > min.at(j) && neg)) eq = false;
            }

            res *= 10;
            res += digits.at(i);
        }

        return res;
    }
};

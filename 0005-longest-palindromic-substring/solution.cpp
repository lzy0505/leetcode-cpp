// 5. Longest Palindromic Substring
// https://leetcode.com/problems/longest-palindromic-substring/
// Difficulty: Medium
// Tags: Two Pointers, String, Dynamic Programming
//
// Given a string s, return the longest palindromic substring in s.
//
//
//
// Example 1:
//
// Input: s = "babad"
// Output: "bab"
// Explanation: "aba" is also a valid answer.
//
// Example 2:
//
// Input: s = "cbbd"
// Output: "bb"
//
//
//
// Constraints:
//
// 	  - 1 <= s.length <= 1000
//
// 	  - s consist of only digits and English letters.
//
//
//

#include <stdio.h>
#include <string>
#include <vector>
using namespace std;

class DynamicProgrammingSolution {

// Complexity O(N^2)
public:

  string longestPalindrome(string s) { 

    //special case: length = 1, true
    if (s.length() <= 1) return s;
    // remember the position of the return
    int res_b = 0, res_l = 1;

    // data structure: two vectors of pairs 
    //   first is if the string is a palindromic
    //   second is if all the chars of a string is identical
    // Instead of a len * len matrix, we reuse vectors to save memory
    // OBS: odd len = true => even len = true or even => odd  
    //      is only possible if all chars are identical

    // len = 1 is always true
    vector<pair<bool, bool>> A(s.length(), {true, true});
    // len = 2
    vector<pair<bool, bool>> B(s.length());

    for (int i = 0; i < B.size() - 1; i ++)
    {
      if (s[i] == s[i+1]) 
      { 
        B[i] = {true, true};
        res_b = i;
        res_l = 2;
      }
    }
    // special case 2: length = 2, return now.
    if (s.length() == 2) return s.substr(res_b, res_l);

    // length >= 3
    auto* L_2 = &A;
    auto* L_1 = &B;
    auto* L = &A;

    for(int len = 3; len <= s.length(); len ++){
      for (int b = 0; b <= s.length() - len; b ++){
        // A[b,l] = true if A[b+1, l-2] = true and s[b] = s[b+ l-1]
        bool cond1 = (*L_2)[b+1].first && s[b] == s[b + len - 1];
        // A[b,l] = true if all char of s[b,l-1] are identical (which implies A[b, l-1] = true), and the char is s[b+l-1]
        bool cond2 = (*L_1)[b].second && s[b + len - 2] == s[b + len - 1];

        if (cond1 || cond2){
          (*L)[b] = {true, cond2};
          res_b = b;
          res_l = len;
        }
        else 
          (*L)[b] = {false, false};
      }
      // update pointers
      L = L_1;
      L_1 = L_2;
      L_2 = L;
    }

    return s.substr(res_b, res_l);
  }
};


class ManacherSolution {

// Complexity O(N)
public:

  string longestPalindrome(string s) { 
     // TODO
  }
};



class StringHashingSolution {

// Complexity O(N * logN)
public:

  string longestPalindrome(string s) { 
     // TODO
  }
};

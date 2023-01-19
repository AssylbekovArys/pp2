#include <bits/stdc++.h>
using namespace std;

int main() {
    string s, s1;
    cin >> s >> s1;
    string s2 = "";
    for(int i = 0; i < s1.size() / s.size(); i++) {
        s2 += s;
    }

    if(s2 == s1) {
        cout << "YES";
    } else {
        cout << "NO";
    }
}
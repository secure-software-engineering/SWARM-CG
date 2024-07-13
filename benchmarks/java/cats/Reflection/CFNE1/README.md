# ClassForNameExceptions
Test cases w.r.t. to classloading using ```Class.forName(className:String)``` and its respective
exceptions to test whether valid path might be ignored which leads to unsoundness.

## CFNE1
[//]: # (MAIN: cfne.Demo)
This test case targets a common try catch pattern when classes are loaded. An existing class is loaded
over ```Class.forName(...)```, instantiated and then casted to another class. Unfortunately, the class
that is instantiated is __incompatible__ with the cast such that the operation results in a
```ClassCastException```.

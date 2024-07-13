[//]: # (MAIN: cfne.Demo)
This test case targets a common try catch pattern when classes are loaded. An absent class is loaded
over ```Class.forName(...)```. Since the class __can't be found__ the operation results in a ```ClassNotFoundException```
which is handled in one of the catch blocks.

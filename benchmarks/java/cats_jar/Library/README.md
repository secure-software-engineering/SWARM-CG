# Library
Tests the call-graph handling for the analysis of software libraries, i.e. partial programs. The main
difference between applications and library software is, that libraries are intended to be used, and,
therefore, to be extended. Library extensions can cause call-graph edges within the library that can
already be detected without a concrete application scenario. For instance, when the library contains yet
independent as well as by client code accessible and inheritable classes and interfaces that declare
a method with exactly the same method signature.
 
When the previous conditions are meet, a client can extend such a class as well as implement the
interface respectively without overriding the respective method which leads to interface call sites
that must be additionally resolved to the class' method. We refer to those edges as call-by-signature
(CBS) edges. 

According to [1], all test cases in that category assume that all packages are closed.
 
[1] Reif et al., Call Graph Construction for Java Libraries, FSE 2016.
# Pattern Matching
From Java 16 onwards, `instanceof` tests can cast the tested objected to an
object of the test target without an explicit cast. Example:

//Before Java 16
if (obj instanceof Rectangle) {
    Rectangle r = (Rectangle) obj;
    int perimeter = 2 * ( r.length() + r.breadth() );
}

//Java 16 pattern matching
    if (obj instanceof Rectangle r) {
    int perimeter = 2 * ( r.length() + r.breadth() );
}

[//]: # (MAIN: pm.Test)
Test to check whether the constructor call during pattern matching is resolved correctly

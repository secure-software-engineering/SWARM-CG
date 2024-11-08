// pm/Test.java
package pm;

import lib.annotations.callgraph.IndirectCall;
class Shape {}

class Rectangle extends Shape {}

class Square extends Shape {
    @IndirectCall(name = "Square", resolvedTargets = "Lpm/Square;")
    public Square() {
        //do something
    }
}

public class Test {
    public static void main(String[] args) {
        Shape s = new Square();
        if(s instanceof Square sq) {
            //do something
        }
    }
}

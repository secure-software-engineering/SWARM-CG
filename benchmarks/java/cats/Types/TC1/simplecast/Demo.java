// simplecast/Demo.java
package simplecast;

class Demo {
    public static void main(String[] args) throws Exception {
        if (args.length == 0) 
          castToTarget(new Target());
        else 
          castToTarget(new Demo());
    }

    static void castToTarget(Object o) {
        Target b = (Target) o;
        b.target();
    }

    public String target() { return "Demo"; }
}
class Target {
  public String target() { return "Target"; }
}

// instanceofclassapi/Demo.java
package instanceofclassapi;

class Demo{ 
    public static void main(String[] args) throws Exception {
        if (args.length == 0) 
          callIfInstanceOfTarget(new Target());
        else 
          callIfInstanceOfTarget(new Demo());
    }

    static void callIfInstanceOfTarget(Object o) {
      if (Target.class.isInstance(o))
        o.toString();
    }

    public String toString() { return "Demo"; }
}
class Target {
  public String toString() { return "Target"; }
}

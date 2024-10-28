// typecasts/CastDemo.java
package typecasts;

class CastDemo {
    public static void main(String[] args) throws Exception {
        if (args.length == 0) 
            castToTarget(new TargetClass());
        else 
            castToTarget(new CastDemo());
    }

    static void castToTarget(Object obj) {
        TargetClass target = (TargetClass) obj;
        target.targetMethod();
    }

    public String targetMethod() { return "CastDemo"; }
}

class TargetClass {
    public String targetMethod() { return "TargetClass"; }
}

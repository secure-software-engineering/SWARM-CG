// castclassapi/Demo.java
package castclassapi;

class Demo {
    public static void main(String[] args) throws Exception {
        if (args.length == 0) 
          castToTarget(Target.class, new Target());
        else 
          castToTarget(Demo.class, new Demo());
    }

    static <T> void castToTarget(Class<T> cls,  Object o) {
        T target = cls.cast(o);
        target.toString();
    }

    public String toString() { return "Demo"; }
}

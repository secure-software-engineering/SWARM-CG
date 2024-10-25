// lrr/Demo.java
package lrr;


class Demo {
    public static void verifyCall(){ /* do something */ }

    public static void main(String[] args) throws Exception {
        String className = (args.length % 2 == 0) ? "lrr.Left" : "lrr.Right"; 
        Class.forName(className);
    }
}

class Left {
    
    static {
        staticInitializerCalled();
    }

    static private void staticInitializerCalled(){
        Demo.verifyCall();
    }
}


class Right {
    
    static {
        staticInitializerCalled();
    }

    static private void staticInitializerCalled(){
        Demo.verifyCall();
    }
}

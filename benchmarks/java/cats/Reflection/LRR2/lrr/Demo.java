// lrr/Demo.java
package lrr;


class Demo {
    public static void verifyCall(){ /* do something */ }

    public static void main(String[] args) throws Exception {
        StringBuilder builder = new StringBuilder("lrr.Is");
        if (args.length % 2 == 0)
            builder.append("Even"); 
        else
            builder.append("Odd");
        String className = builder.toString();
        Class.forName(className);
    }
}

class IsEven {
    
     static {
         staticInitializerCalled();
     }

     static private void staticInitializerCalled(){
         Demo.verifyCall();
     }
 }


 class IsOdd {

     static {
         staticInitializerCalled();
     }

     static private void staticInitializerCalled(){
         Demo.verifyCall();
     }
 }

// invokedynamic/LambdaDemo.java
package invokedynamic;

import java.util.function.Function;

class LambdaDemo {
    public static void main(String[] args) {
        Function<Integer, Boolean> checkEven = (Integer num) -> {
            performAction();
            return num % 2 == 0;
        };
        checkEven.apply(2);
    }

    private static void performAction() {
        // call in lambda
    }
}
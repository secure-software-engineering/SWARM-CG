// dp/Main.java
package dp;

import java.lang.reflect.Method;


public class Main {
	public static void main(String[] args) {
		Foo foo = (Foo) DebugProxy.newInstance(new FooImpl());
		foo.bar(null);
	}
}
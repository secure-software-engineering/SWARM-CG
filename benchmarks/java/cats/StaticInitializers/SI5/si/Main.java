// si/Main.java
package si;

public class Main{

	public static void main(String[] args) {
		new Demo();
	}
}

class Demo {

	static {
		init();
	}

	static void init() {
		callback();
	}

	static void callback() {}
}

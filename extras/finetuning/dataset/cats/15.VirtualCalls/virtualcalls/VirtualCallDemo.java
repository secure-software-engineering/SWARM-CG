// virtualcalls/VirtualCallDemo.java
package virtualcalls;

interface CallInterface {
    void performAction();
}

class VirtualCallDemo implements CallInterface {

    public static CallInterface[] instances = new CallInterface[]{new VirtualCallDemo(), new CallImpl()};

    public void performAction() { }

    public static void main(String[] args) {
        CallInterface instance = instances[0];
        instance.performAction();
    }
}

class CallImpl implements CallInterface {
    public void performAction() { }
}
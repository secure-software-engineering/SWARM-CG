[//]: # (MAIN: id.Class)
Tests the invocation of a lambda that was first written to and then retrieved from an array. This 
case results in an invokedynamic with an *INVOKESTATIC* method handle where the receiver argument
is read by *AASTORE* instruction form an array before the method invocation takes place.

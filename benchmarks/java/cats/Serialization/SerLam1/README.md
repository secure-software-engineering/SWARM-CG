# Serialization and Lambdas
Tests Java's serialization mechanism when Lambdas are (de)serialized, i.e., de(serialization) of Lambdas
causes the JVM to use ```java.lang.invoke.SerializedLambda```.

[//]: # (MAIN: serlam.DoSerialization)
Tests whether the serialization of lambdas that implement a functional interface is modelled correctly.

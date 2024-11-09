[//]: # (MAIN: castclassapi.Demo)
Type narrowing due to previous cast using Java's class API. The method ```castclassapi.Demo.castToTarget```
takes a class object that is parameterized over the type the cast should be performed to and an object
that will be casted within the method. It then casts it via ```Class.cast``` to ```castclassapi.Target```
and then calls ```toString``` on the casted object which rules out ```castclassapi.Demo.toString``` as receiver.

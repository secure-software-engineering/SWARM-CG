[//]: # (MAIN: id.Class)
Tests an invokedynamic invocation where the object receiver is captured in a lambda function.
Declaring a lambda function in another class (cf. ```id.LambdaProvider```) as it is invoked
(cf. ```id.Class```) leads to an *INVOKESTATIC* method handle where the receiver is not declared
within the same class.

Java method signature: [Fullname of Class]:[method name]([Parameterlist])
Parametertypes use also the full name of the class.

The json file consits of a list of method signatures that define the caller. 
Each caller has a list of called methods. 
They are defined by an object containing target and direct. 
target saves the method signature of the called method and direct saves an bool defining if the caller directly or indirectly called the target.

The json file contains only edges that are defined by annotations in the cat benchmark  


JSON Progress
- [x] Classloading
- [ ] ContextSensitivity
- [ ] DynamicProxies
- [ ] FieldSensitivity
- [ ] FlowSensitivity
- [ ] Java8InterfaceMethods
- [ ] Java8Invokedynamics
- [ ] JVMCalls
- [ ] Library
- [ ] ModernReflection
- [ ] NonVirtualCalls
- [ ] ObjectSensitivity
- [ ] PatternMatching
- [ ] PrivateInterfaceMethods
- [ ] Records
- [ ] Reflection
- [ ] Serialization
- [ ] SignaturePolymorphicMethods
- [ ] StaticInitializers
- [ ] Types
- [ ] Unsafe
- [ ] VirtualCalls
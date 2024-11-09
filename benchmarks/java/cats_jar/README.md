Java method signature: [Fullname of Class]:[method name]([Parameterlist])
Parametertypes use also the full name of the class.

The json file consits of a list of unnamed objects that define the calls. 
Each call is defined by a caller signature and a list of targets.
A list element in the targets list consits of a callee defining the target of the call with a signature, a boolean saying if it is direct or indirect call and a line number of the call in the caller. 


The json file contains only edges that are defined by annotations in the cat benchmark  

Structure:

[
	{
		"caller":"signature",
		"targets":
			[
				{
					"callee":"signature1",
					"direct":false,
					"line":0
				},
                				{
					"callee":"signature2",
					"direct":false,
					"line":0
				}
			]
	},
    {
		"caller":"signature4",
		"targets":
			[
				{
					"callee":"signature5",
					"direct":false,
					"line":0
				}
			]
	}
]
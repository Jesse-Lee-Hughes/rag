# memory
The memory system seems to have some bugs. 
- clear memory doesn't actually clear all of the memory for my specific conversation
- Memory seems to be very much about the context provided less about the responses given and question etc. The user shoulndn't really be aware of the context given as much as the interaction with the LLM.

# features
- implement a user role based context that would work as follows: if user role = x "I am an Engineer looking to perform the following activities as part of my role [abc, xyz] i have read write access to the following systems: [network devices]. I am not allowed to interact with the following ssystems: [accounting, payroll]
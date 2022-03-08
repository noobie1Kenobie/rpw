# rpw
Ranked Positional Weight Method coded in Python

The python script created here is intended to provide a solution for optimization in a Simple Assembly Line Problem. 
It is able to solve for any configuration of assembly lines, with certain limitations. The limitations are:
  1. Within the assembly lines process, there are no loop back processes. 
  (That's all the limitation that I can think of right now)
This script was developed and tested on a linux environment. So, I'm not too sure about MS and MAC environment. 
Therefore all the instructions will be relevant to linux. For the other OSes, you need to adapt, or maybe later
I'd add the relevent instructions.

This can be a helpful teaching and learning aid for industrial practitioners. 

Arguments has been put out that this type of optimization is for manual processes only. That is not true, as it is
relevant in the automated environment as well. During the initial stages of processing station design and arrangements, 
this type of optimization is needed. It can cut down the overall processing time per unit. 
This type of optimization can also be applied to Business Processes as well. 

The following are the instructions of how to use this code:
Make a directory. The script will search the directory for the relevant text files to process. 

These are the inputs for the script.
1. You need this scripts (obvious).
2. Assembly process in digraph. The node connections are to be described in 
   text format. Look at the example. Name this file as edges_nodes.txt.
3. The number of hours available to work on the process in a year, name this file as demand_worktime.txt.
4. The time it takes for each process to complete. Name this file as tasktime.txt.
5. The name of each of the processes involved. Name this file as tasknames.txt.

The structure of the file and directories would be:
<directory>main_script.py
  +-<directory for input files>
    - edges_nodes.txt
    - demand_worktime.txt
    - tasktime.txt
    - tasknames.txt
One of the important part of this whole exercise is to ensure that the time units are correct. You will need
to specify the unit in time, sec/min/hours/days, during the script execution. 
The command to execute this script:
  python /directory/for/python/RankedPositionalWeightMethod.py -d /directory/for/python/file/<example> -u min
  
The output of from this script are:
1. The new assembly line process with task combined, based on the takt time.
2. The new assembly line process with task combined, base on the the highest processing time.
3. Efficiency graph for the 2 proposed solutions above and the unbalanced assembly line. 
4. Report on the assembly line problem and it's proposed solution, in simple text file.

It is important to note that the proposed solution provided by this script is only one of the possible solution for 
the assembly line balancing problem. Therefore the solution presented here might not be 'final' or the best solution
for the input assembly line problem, it is just one possible solution for the problem. Using other methods to obtain
a solution for the assembly line problem would yield a different solution. Some research are dedicated to in comparing
the efficiency produced by different types of 'algorithm' in simple assembly line problems. 

  
Slava Ukraini

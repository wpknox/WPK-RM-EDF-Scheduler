# WPK-RM-EDF-Scheduler
Creates RM and EDF schedules for a user given task set if possible.

**Author** Willis Knox

Used [this similar project](https://github.com/diegoperini/py-common-scheduling-algorithms) as a reference when initally starting to make sure I was keeping things 'pythonic'
### RMS Utilization Check and EDF Scheduability Check
First runs the basic RMS scheduablility check (utilization check) to see if the task set passes a sufficient, but not necessary test for RM scheduling. 
The basic RM utilization check is determined by the following equation:

<img src="https://latex.codecogs.com/gif.latex?\sum\frac{c_i}{p_i}&space;\leq&space;n(2^{\frac{1}{n}}&space;-&space;1)" title="\sum\frac{c_i}{p_i} \leq n(2^{\frac{1}{n}} - 1)" />

Where <img src="https://latex.codecogs.com/gif.latex?c_i" title="c_i" /> is the **worst case execution time** for a task *i*, <img src="https://latex.codecogs.com/gif.latex?p_i" title="p_i" />
is the **period** for a task *i*, and **n** is the number of tasks in the task set.

If the task set passes this test, then it is also scheduable by the EDF algorithm because the **EDF scheduability check** is less strict. It is:

<img src="https://latex.codecogs.com/gif.latex?\sum\frac{c_i}{p_i}&space;\leq&space;1" title="\sum\frac{c_i}{p_i} \leq 1" />
and
<img src="https://latex.codecogs.com/gif.latex?n(2^{\frac{1}{n}}&space;-&space;1)&space;\leq&space;1&space;\,\,\,\,\forall&space;n&space;\geq&space;1,&space;n&space;\in&space;\{1,2,3,...\}" title="n(2^{\frac{1}{n}} - 1) \leq 1 \,\,\,\,\forall n \geq 1, n \in \{1,2,3,...\}" />

---

### RMS Exact Analysis
If a task set fails the RMS utilization check, it may still be schedulable by RM or EDF. Before testing the exact analysis,
the program directly tests the **EDF scheduability check** mentioned above. If the task set passes, then it can be *at least* scheduled by EDF.

After this, the program will then preform the **RMS Exact Analysis** test to determine if it can also be scheduled with the RM algorithm. I could have skipped over the basic
RM utilization test and ran the task set against this test, but by not skipping over the utilization test, I potentionally save the computer from running unneeded calculations.

The RM Exact Analysis formula is used on every task in the task set:

<img src="https://latex.codecogs.com/gif.latex?W_i(t)&space;=&space;\sum_{j&space;=&space;1}^ic_j&space;\times&space;\left&space;\lceil&space;\frac{t}{p_j}&space;\right&space;\rceil" title="W_i(t) = \sum_{j = 1}^ic_j \times \left \lceil \frac{t}{p_j} \right \rceil" />

A task passes this test if, for the task *i*:

<img src="https://latex.codecogs.com/gif.latex?W_i(t_k)&space;=&space;t_k" title="W_i(t_k) = t_k" />

If a *t* is greater than the largest *p* for a task, the task fails this test. Which means that the task set is not RM scheduable.

<img src="https://latex.codecogs.com/gif.latex?\frac{t}{p}&space;>&space;1" title="\frac{t}{p} > 1" />

---

### Displaying Information
After running the above test, the program will `print` scheduling information to the user. If the task set cannot be scheduled, it will print a message tell the user that it 
is not scheduable.

If the task set *can* be scheduable by one or both of the algorithms, the program will then go on to create the schedule for the user given tasks. This is done by creating
`TaskInstance` objects that represent each instance of each task for a schedule. 

The created schedules will be printed out to the user in a basic format in the terminal, but more importantly, actual `matplotlib` graphs will be created showing the 
created schedules. Displaying these graphs to the user helps them visualize how the tasks would be scheduled by the algorithms.

For example, if a user entered the following tasks:
- Task 1: (c = 1, p = 3)
- Task 2: (c = 4, p = 6)

They would see the following two graphs:

![RM Schedule](https://github.com/wpknox/WPK-RM-EDF-Scheduler/blob/master/example_rm.png)

![EDF Schedule](https://github.com/wpknox/WPK-RM-EDF-Scheduler/blob/master/example_edf.png)

As you can see, the schedules are slightly different, but this task set can be scheduled by both algorithms.

---

### Python Version
\>= 3.9.0

This is required to correctly run this program because I use `math.lcm`, which is new to 3.9.0. If you use an earlier version of Python, the program will fail to run.

### How to Run

```
python schedule.py
```

If you are on Windows and do not have Python in your PATH, you will need to specify the exact location on your computer where your Python installation is to run the program.

import sys
import copy
import math
import random
import pandas as pd
import matplotlib.pyplot as plt

CLOCK_CYCLE = 1

class Task(object):
  def __init__(self, name, period, wcet) -> None:
    self.name = name
    self.period = period    
    self.wcet = wcet
  
  def __str__(self) -> str:
    return "<class 'Task'>: {'name':'%s', 'period':'%s', 'wcet':'%s'}" % (self.name, self.period, self.wcet)
  
  def __repr__(self) -> str:
    return str(self.__class__) + ": " + str(self.__dict__)
  
  def update_edf_period(self, curr_iter):
    self.period += self.period / curr_iter

class TaskInstance(object):
  def __init__(self, task, priority, start, end) -> None:
    self.task = task
    self.usage = 0
    self.start = start
    self.end = end
    self.priority = priority
    self.id = random.randint(0, 1000)
  
  def execute(self, usage) -> bool:
    self.usage += usage
    if self.usage >= self.task.wcet:
      return True
    return False
  
  def __repr__(self) -> str:
    return str(self.task.name) + "#" + str(self.id) + ": Remaining execution time: " + str(self.task.wcet - self.usage) + \
          " Start Time: " + str(self.start) +" Deadline: " + str(self.end) + " Priority: " + str(self.priority)
  
  def get_name(self):
    return str(self.task.name) + "#" + str(self.id)


def get_user_input(text):
  """Function to prompt the user with a given text string and ask them to input an integer used to in the making of tasks

  Args:
      text (string): Message to display to the user telling them what to input

  Returns:
      int: Integer value that the user entered at the prompt. Exits out of program if user fails to enter an approriate integer value
  """
  user_input = input(text)
  ret = 0
  try:
    ret = int(user_input)
  except:
    print("Input must be an integer")
    sys.exit()
  if ret > 0:
    return ret
  else:
    print("Input must be an integer greater than 0")
    sys.exit()

def priority_cmp(e):
  return e.priority

def task_period(e):
  return e.period

def calc_cp(task_list) -> int:
  cp = 0
  for task in task_list:
    cp += task.wcet / task.period
  return cp

def find_lcm(tasks):
  periods = []
  for task in tasks:
    periods.append(task.period)
  return math.lcm(*periods)

def create_tasks(num_tasks):
  """Creates all tasks depending on what the user enters.

  Args:
      num_tasks (int): Number of tasks to make

  Returns:
      List[Task]: Returns a list of Tasks that the program will try to create EDF and RM schedules for
  """
  tasks = []
  for i in range(0, num_tasks):
    i_str = str(i + 1)
    text = "Enter the worst case execution time for task " + i_str + ": "
    wcet = get_user_input(text)
    text = "Enter the period for task " + i_str + ": "
    period = get_user_input(text)
    t_name = "Task "+ i_str
    tasks.append(Task(name=t_name, period=period, wcet=wcet))
  return tasks

def rms_utilization_check(frac, num_tasks) -> bool:
  """Checks to see if the given task set passes the sufficient, but not necessary RMS schedulability check.
  If this is passed, then we know that the Task Set is schedulable by both EDF and RMS, and we do not need to perform any more checks.

  Args:
      frac (float): Sum of all of the wcet/periods of the tasks in the task set. This number must be less than a specific value depending on num_tasks to
                    pass this check
      num_tasks (int): Number of tasks in the task set

  Returns:
      boolean: True or False value whether or not the task set passes the RMS utilization check
  """
  return frac <= num_tasks*(2**(1/num_tasks) - 1)

def rms_exact_analysis(tasks) -> bool:
  """If the task set fails the rms_utilization_check, it may still be scheduable, and exact analysis by the Completion Time Test needs to be performed.
  Method performs the completion time test on each task in the task set. If all tasks pass, then the task set can be scheduled by RMS, if any of the tasks
  fail, then the entire task set fails and cannot be scheduled.

  Args:
      tasks (List[Task]): List of Task objects that need to be analyzed by the test

  Returns:
      boolean: True or False value whether or not the task set passes the Completion Time Test
  """
  rms = copy.deepcopy(tasks)
  rms.sort(key=task_period)
  # go through each task in priority order and perform exact analysis
  for i in range(len(rms)):
    old_t = 0
    curr_tasks = rms[:i+1] # get list of tasks for exact analysis for current task
    for t in curr_tasks:
      old_t += t.wcet # find t_0
    while old_t <= rms[i].period:
      new_t = 0
      for j in range(len(curr_tasks)): 
        new_t += curr_tasks[j].wcet * math.ceil(old_t/curr_tasks[j].period) # calc t_1, t_2, ..., t_n depending on cycle
        
      if new_t == old_t: # if new is the same as old, this task is good
        break
      if new_t > rms[i].period: # if new is larger than period, this task set isn't possible... tell user this
        print("********************************************************************************************************************")
        print("On", rms[i].name, "exact analysis failed, so a RM schedule cannot be made for the task set")
        print()
        print("Failing 't' value:", new_t, "\twhich was more than the maximum:", rms[i].period)
        print("********************************************************************************************************************")
        return False
      old_t = new_t # if new_t < old_t, set old_t to new_t and repeat while loop
  return True

def create_graph(data, tasks, labels, lcm, title):
  """Creates a matplotlib graph for the given tasks

  Args:
      data (List[dict]): List of dictionaries to be turned into a DataFrame object. The dicts contain information about each Task Instance
      tasks (List[Task]): List of scheduled tasks
      labels (List[str]): Names of each task that is scheduled
      lcm (int): Least Common Multiple. Used to determine how far the graph should display
  """
  ROW_TOTAL_HEIGHT = 12
  TASK_HEIGHT = 6
  
  ticks = []
  for i in range(len(tasks)):
    ticks.append(TASK_HEIGHT + i*ROW_TOTAL_HEIGHT)
  df = pd.DataFrame(data)
  print(df)
  gnt = plt.subplot()
  gnt.set_xlim(0, lcm)
  gnt.set_ylim(0, ROW_TOTAL_HEIGHT*len(tasks))
  gnt.set_yticks(ticks)
  gnt.set_yticklabels(labels)
  gnt.set_xlabel('Time')
  gnt.set_ylabel('Task')
  gnt.grid(True)
  gnt.title.set_text(title)
  graph_dict = {}
  for i in range(0, df.shape[0]):
    dur = df.iloc[i, 2] - df.iloc[i, 1]
    start = df.iloc[i, 1]
    
    resource = df.iloc[i, 3]
    if resource in graph_dict:
      graph_dict[resource].append((start, dur))
    else:
      graph_dict[resource] = [(start, dur)]
  
  k = 0
  for key in graph_dict:
    gnt.broken_barh(graph_dict[key], ((TASK_HEIGHT//2) + k * ROW_TOTAL_HEIGHT, TASK_HEIGHT))
    k += 1
  plt.show()

def make_rms(rms_task_list, lcm):
  """Creates the RM schedule for the task set. Only called if the task set has already been proven by either the utilization check
  or exact analysis to be schedulable by RM algorithm.

  Args:
      rms_task_list (List[Task]): Task set to schedule
  """
  print("================================================================================================================")
  rms_tasks = copy.deepcopy(rms_task_list)
  rms_tasks.sort(key=task_period)
  task_insts = []
  labels = []
  data_list = []
  for task in rms_tasks:
    labels.append(task.name)
    num_inst = lcm // task.period
    for j in range(0, num_inst):
      task_insts.append(TaskInstance(task, task.period, j * task.period, (j + 1) * task.period))
  for i in range(0, lcm):
    possible_ti = []
    for ti in task_insts:
      if ti.start <= i:
        possible_ti.append(ti)
    possible_ti.sort(key=priority_cmp)
    if len(possible_ti) > 0:
      print(possible_ti)
      curr_ti = possible_ti[0]
      data_list.append(dict(Task=curr_ti.id, Start=i, End=i+1, Resource=curr_ti.task.name))
      print("Before:", curr_ti, "start sec: ", i)
      if curr_ti.execute(CLOCK_CYCLE):
        task_insts.remove(curr_ti)
      print("After:", curr_ti, "end sec: ", i + 1)
      print("================================================================================================================")
  title = "RMS Schedule"
  create_graph(data_list, rms_tasks, labels, lcm, title)

def make_edf(edf_task_list, lcm):
  """Creates the EDF schedule for the task set. Only called if the task set has already been proven by the EDF scheduability check to be scheduable
  with the EDF algorithm

  Args:
      rms_task_list (List[Task]): Task set to schedule
  """
  edf_tasks = copy.deepcopy(edf_task_list)
  edf_tasks.sort(key=task_period)
  task_insts = []
  labels = []
  data_list = []
  for task in edf_tasks:
    labels.append(task.name)
    num_inst = lcm // task.period
    for j in range(0, num_inst):
      task_insts.append(TaskInstance(task, (j * task.period) + task.period, j * task.period, (j + 1) * task.period))
  for i in range(0, lcm):
    possible_ti = []
    for ti in task_insts:
      if ti.start <= i:
        possible_ti.append(ti)
    possible_ti.sort(key=lambda x: (x.priority, x.start))
    if len(possible_ti) > 0:
      print(possible_ti)
      curr_ti = possible_ti[0]
      data_list.append(dict(Task=curr_ti.id, Start=i, End=i+1, Resource=curr_ti.task.name))
      print("Before:", curr_ti, "start sec: ", i)
      if curr_ti.execute(CLOCK_CYCLE):
        task_insts.remove(curr_ti)
        for ti in task_insts:
          if ti.task.name == curr_ti.task.name and ti.end == curr_ti.end + curr_ti.task.period:
            ti.start = i + 1
            break
      print("After:", curr_ti, "end sec: ", i + 1)
      print("================================================================================================================")
  title = "EDF Schedule"
  create_graph(data_list, edf_tasks, labels, lcm, title)

if __name__ == '__main__':
  task_cnt = get_user_input("Enter the number of tasks to schedule: ")
  task_list = create_tasks(task_cnt)
  c_over_p = calc_cp(task_list)
  period_lcm = find_lcm(task_list)
  if rms_utilization_check(c_over_p, task_cnt) or (c_over_p <= 1 and rms_exact_analysis(task_list)):
    print("schedule both")
    # first make rms schedule
    make_rms(task_list, period_lcm)
    # now make edf schedule
    make_edf(task_list, period_lcm)
  elif c_over_p <= 1:
    print("EDF only")
    make_edf(task_list, period_lcm)
  elif rms_exact_analysis(task_list):
    print("RMS only")
    make_rms(task_list, period_lcm)
  else: # Task Set can't be scheduled by either algorithm
    print("********************************************************************************************************************")
    print("Task set fails EDF scheduability check because", c_over_p, "> 1")
    print()
    print("Neither an EDF nor RM schedule can be made for the given task set!")
    print("********************************************************************************************************************")
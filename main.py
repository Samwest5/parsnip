import subprocess
import sys

def makeColor(commit, colorCode):
  """
  Wraps each commit message in color formatting to change its
  color when displayed in the console.
    Args:
      commit: String containing a commit's abreviated hash and message.
      colorCode: Integer of value 0 - 3.
    Returns:
      String containing commit's abreviated hash and message
      wrapped in the matching color formatting.
  """
  # red
  if colorCode == 0:
    return f'\033[91m{commit}\033[00m'
  # yellow
  if colorCode is 1:
    return f'\033[93m{commit}\033[00m'
  # green
  if colorCode is 2:
    return f'\033[92m{commit}\033[00m'
  # cyan
  if colorCode is 3:
    return f'\033[96m{commit}\033[00m'

# Pipe the git log on the passed branch and return the abbreviated hashes with messages
def retreive_log(branch):
  """
  In a subprocess retrieves the formatted git log of whatever branch
  name has been passed into the function.
  Args:
    branch: String of name of git branch.
  Returns: String containing commit's abreviated hash and message.
  Raises:
    CalledProcessError: An error occurred while running command in subprocess.
  """
  try:
    log = subprocess.run(f'git log {branch} --pretty=format:"%h %s"',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        check=True)
  except subprocess.CalledProcessError:
    print(f'Error with retrieving log for branch "{branch}"')
    sys.exit()
  return log.stdout.decode().splitlines()

def get_current_branch():
  """
  In a subprocess retrieves the current branch name to be used as
  one of the logs to compare against if only one argument was passed
  when the script began. 
  Returns: String containing current branch name
  Raises:
    CalledProcessError: An error occurred while running command in subprocess.
  """
  try:
    log = subprocess.run(f'git branch --show-current',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        check=True)
  except subprocess.CalledProcessError:
    print('Error with retrieving current branch')
    sys.exit()
  return log.stdout.decode().strip()

def reduce_text_length(logs):
  """
  Truncates the length of every commmit message to avoid cluttering the
  console window. 
  Args:
    logs: List of strings. Each element contains the commit's
      abreviated hash and message.
  Returns:
    List of strings. Each element contains the commit's abreviated hash
    and shortened message.
  """
  trimmed_logs = []
  for i in range(len(logs)):
    trimmed_logs.append([])
    for j in range(len(logs[i])):
      if j == 0:
        trimmed_logs[i].append(logs[i][j])
      else:
        parts = logs[i][j].split(' ', 1)
        if len(parts[1]) > 31:
          parts[1] = parts[1][:28] + '...'
        trimmed_logs[i].append(" ".join(parts))
  return trimmed_logs

def get_color_maps(logs):
  """
  Each commit from the left log is compared against every commit
  from the right log. Commits that share a common hash are labled 
  with 2-green. Commits that share a common message but do not share a hash
  are labeled with 1-yellow. ALl other commits are labeled with 0-red. 
  Args:
    logs: List of strings. Each element contains the commit's
      abreviated hash and message.
  Returns: 
    Tuple of two lists containing integers representing the 
      left and right logs. Each integer corresponds to a color 
      that the log entries will later be wrapped in.
  """
  left = logs[0]
  color_map_1 = [None] * len(left)
  right = logs[1]
  color_map_2 = [None] * len(right)
  color_map_1[0] = 3
  color_map_2[0] = 3
  for i, commit_1 in enumerate(left):
    if i == 0:
      continue
    left_hash, left_message = commit_1.split(' ', 1)
    for j, commit_2 in enumerate(right):
      if j == 0:
        continue
      right_hash, right_message = commit_2.split(' ', 1)
      if color_map_2[j]:
        continue
      if left_hash == right_hash:
        color_map_1[i] = 2
        color_map_2[j] = 2
        break
      elif left_message == right_message:
        color_map_1[i] = 1
        color_map_2[j] = 1
    for i, color in enumerate(color_map_1):
      if not color:
        color_map_1[i] = 0
    for i, color in enumerate(color_map_2):
      if not color:
        color_map_2[i] = 0
  return color_map_1, color_map_2

def color_logs(color_maps, logs):
  """
  Wraps each of the commits in each log in color formatting.
  Args:
    color_maps: List of two lists containing integers representing the 
      left and right logs. Each integer corresponds to a color that the log entries
      will later be wrapped in.
    logs: List of strings. Each element contains the commit's
      abreviated hash and message.
  Returns:
    A list containing the two logs with each of their string elements now wrapped 
    in  color formatting.
  """
  left_logs = logs[0]
  left_map = color_maps[0]
  right_logs = logs[1]
  right_map = color_maps[1]
  for i, commit in enumerate(left_logs):
    left_logs[i] = makeColor(commit, left_map[i])
  for i, commit in enumerate(right_logs):
    right_logs[i] = makeColor(commit, right_map[i])
  return [left_logs, right_logs]

def reduce_logs_length(logs, color_maps):
  """
  Finds the furthest point in either branch chronologically where the 
  commits no longer have any differences and sets that as the 
  cutoff point where the logs will stop being displayed.
  Args:
    logs: List of strings. Each element contains the commit's
      abreviated hash and message.
    color_maps: List of two lists containing integers representing the 
      left and right logs. Each integer corresponds to a color that the log entries
      will later be wrapped in.
  Returns:
    A tuple containing the truncated logs and color_maps arguments.
  """
  left_map, right_map = color_maps
  left_log, right_log = logs
  last_left_difference = len(left_map) - 1
  last_right_difference = len(right_map) - 1
  for i, color in enumerate(left_map):
    if color == 0 or color == 1:
      last_left_difference = i
  for i, color in enumerate(right_map):
    if color == 0 or color == 1:
      last_right_difference = i
  max_last_difference = max(last_left_difference, last_right_difference)
  left_map = left_map[:max_last_difference + 2]
  left_log = left_log[:max_last_difference + 2]
  right_map = right_map[:max_last_difference + 2]
  right_log = right_log[:max_last_difference + 2]
  return [left_log, right_log], [left_map, right_map]

def display_logs(colored_logs):
  """
  Prints the commits from each log side by side.
  To keep the script cross-platform all formatting is done 
  within the script use of terminal commands is avoided.
  Args:
    colored_logs: List of strings. Each element contains the commit's
      abreviated hash and message wrapped in a color formatting.
  Returns: 
    None
  """
  MAX_PADDING = 55
  left = colored_logs[0]
  right = colored_logs[1]
  max_length = max(len(left), len(right))
  for i in range(max_length):
    if i >= len(right):
      print(left[i])
    elif i >= len(left):
      print(MAX_PADDING * " " + right[i])
    else:
      padding = MAX_PADDING - len(left[i])
      print(left[i] + padding * " " + right[i])

def valid_number_of_arguments(args):
  return 0 < len(args) < 3

def get_logs(args):
  """
  Calls retrieve_log() to convert each argument into its corresponding git log.
  Args:
    args: A list of strings with each string one of the arguments from sys.argv.
  Returns:
    A list of strings with each string containing 
    the commit's abreviated hash and message.
  """
  logs = []
  if len(args) == 1:
    current_branch = get_current_branch()
    logs.append([current_branch] + retreive_log(current_branch))
  for arg in args:
    logs.append([arg] + retreive_log(arg))
  return logs

def run_script():
  """
  Entry point into script from which all other functions are called
  """
  logs = []
  args = sys.argv[1:]
  if valid_number_of_arguments(args):
    logs = get_logs(args)
    logs = reduce_text_length(logs)
    color_maps = get_color_maps(logs)
    logs, color_maps = reduce_logs_length(logs, color_maps)
    colored_logs = color_logs(color_maps, logs)
    display_logs(colored_logs)
  else:
    print("Error with number of arguments - must pass between 1-2")
  
if __name__ == "__main__":
  run_script()

import subprocess
import sys

def makeColor(commit, colorCode):
  # red
  if colorCode == 0:
    return f'\033[91m{commit}\033[00m'
  # green
  if colorCode is 1:
    return f'\033[92m{commit}\033[00m'
  # yellow
  if colorCode is 2:
    return f'\033[93m{commit}\033[00m'
  # cyan
  if colorCode is 3:
    return f'\033[96m{commit}\033[00m'

# Pipe the git log on the passed branch and return the abbreviated hashes with messages
def retreive_log(branch):
  try:
    log = subprocess.run(f'git log {branch} --pretty=format:"%h %s"',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        check=True)
  except subprocess.CalledProcessError:
    print(f'Error with retrieving log for branch "{branch}"')
    sys.exit()

  return log.stdout.decode().splitlines()

# if only 'other' branch is provided find current branch name
def get_current_branch():
  try:
    log = subprocess.run(f'git branch --show-current',
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        check=True)
  except subprocess.CalledProcessError:
    print('No current branch found')
    sys.exit()

  return log.stdout.decode().strip()

# Reduce the length of all commit messages to 22 characters
# and append "..." if it needs to be truncated to show it was reduced
# for cleaner console display
def trim_length(logs):
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

def colorLogs(logs):
  pass

def display_logs(logs):
  trimmed_logs = trim_length(logs)
  MAX_PADDING = 45
  left = trimmed_logs[0]
  right = trimmed_logs[1]
  max_length = max(len(left), len(right))
  for i in range(max_length):
    # temporary hardcoded. remove when everything is done in other function
    if i == 0:
      padding = MAX_PADDING - len(left[i])
      print(makeColor(left[i], 3) + padding * " " + makeColor(right[i], 3))
    elif i >= len(right):
      print(left[i])
    elif i >= len(left):
      print(MAX_PADDING * " " + right[i])
    else:
      padding = MAX_PADDING - len(left[i])
      print(left[i] + padding * " " + right[i])
    
def run():
  logs = []
  args = sys.argv[1:]

  if len(args) > 2:
    print('Too many branches')
    sys.exit()
  elif len(args) == 0:
    print('Too few branches')
    sys.exit()
  elif len(args) == 1:
    current_branch = get_current_branch()
    logs.append([current_branch] + retreive_log(current_branch))

  for arg in args:
    logs.append([arg] + retreive_log(arg))

  display_logs(logs)

if __name__ == "__main__":
  run()

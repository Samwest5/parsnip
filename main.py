import subprocess
import sys


def makeColor(commit, colorCode):
    """ Set colors for commit. Takes a commit and a color code, then returns
    the colored commit """

    # red
    if colorCode == 0:
        return f'\033[91m{commit}\033[00m'

    # green
    if colorCode == 1:
        return f'\033[92m{commit}\033[00m'

    # yellow
    if colorCode == 2:
        return f'\033[93m{commit}\033[00m'

    # cyan
    if colorCode == 3:
        return f'\033[96m{commit}\033[00m'


def retreive_log(branch):
    """ Pipe the git log on the passed branch and return
      the abbreviated hashes with messages """

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
    """ Creates 'git branch' subprocess. returns stripped str """
    try:
        log = subprocess.run(f'git branch --show-current',
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=True)
    except subprocess.CalledProcessError:
        print('No current branch found')
        sys.exit()

    return log.stdout.decode().strip()


def trim_length(logs):
    """ Reduce the length of all commit messages to 31 characters
    and append '...' if it needs to be truncated to show it was reduced
    for cleaner console display
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
    """ Determine what the coloring of each commit should be
    by iterate each commit from the left log and
    comparing against the commits from the right log
    """

    first = logs[0]
    color_map_1 = [None] * len(first)
    second = logs[1]
    color_map_2 = [None] * len(second)
    color_map_1[0] = 3
    color_map_2[0] = 3
    for i, commit_1 in enumerate(first):
        if i == 0:
            continue
        first_hash, first_message = commit_1.split(' ', 1)
        for j, commit_2 in enumerate(second):
            if j == 0:
                continue
            second_hash, second_message = commit_2.split(' ', 1)
            if color_map_2[j]:
                continue
            if first_hash == second_hash:
                color_map_1[i] = 1
                color_map_2[j] = 1
                break
            elif first_message == second_message:
                color_map_1[i] = 2
                color_map_2[j] = 2
        for i, color in enumerate(color_map_1):
            if not color:
                color_map_1[i] = 0
        for i, color in enumerate(color_map_2):
            if not color:
                color_map_2[i] = 0
    return color_map_1, color_map_2


def color_logs(color_maps, logs):
  
    left_logs = logs[0]
    left_map = color_maps[0]
    right_logs = logs[1]
    right_map = color_maps[1]
    for i, commit in enumerate(left_logs):
        left_logs[i] = makeColor(commit, left_map[i])
    for i, commit in enumerate(right_logs):
        right_logs[i] = makeColor(commit, right_map[i])
    return [left_logs, right_logs]


def display_logs(logs):
    """ Displays and formats logs """
    trimmed_logs = trim_length(logs)
    color_maps = get_color_maps(trimmed_logs)
    colored_logs = color_logs(color_maps, trimmed_logs)
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

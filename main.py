import sys

from get_current_branch import get_current_branch
from retrieve_log import retreive_log
from display_logs import display_logs


def run():
    logs = []
    args = sys.argv[1:]

    if len(args) > 2:
        print('Too many branches')
        sys.exit()
    elif len(args) == 0:
        print('Too few branches')
        # sys.exit()
        current_branch = get_current_branch() # calls git branch --show-current
        logs.append([current_branch] + retreive_log(current_branch)) # calls git log *currentbranch*
        display_logs(logs)
        print("sa")
        sys.exit()
    elif len(args) == 1:
        current_branch = get_current_branch() # calls git branch --show-current
        logs.append([current_branch] + retreive_log(current_branch)) # calls git log *currentbranch*

    for arg in args:
        logs.append([arg] + retreive_log(arg)) # appends [arg] and log to logs

    display_logs(logs)


if __name__ == "__main__":
    run()

import sys
import getopt
from master_robot import RobotAdmin

if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'e:', ['env='])
    env = ''
    for k, v in optlist:
        if k == '-e' or k == '--env':
            env = v
    if env != '':
        robot_admin = RobotAdmin(env=env)
        robot_admin.run()
    else:
        print('[ERROR] lack env config')

# TODO: saveImgTo, dataBase should be populated on the fly


if __name__ == "__main__":
    import subprocess
    import time
    import sys
    DETACHED_PROCESS = 0x00000008

    pid = subprocess.Popen([sys.executable, "C:\\Users\\aakas\\Desktop\\Konduri Work\\vista-gui\\vista_gui\\call_vista_core.py"],
                           creationflags=DETACHED_PROCESS)

    t = 0
    while t < 15:
        time.sleep(1)
        t += 1
        # print pid.communicate()
        print pid.pid, pid.returncode
        print ("Waiting for second: {0}".format(t))

    pid.terminate()
    print "Outside the loop and closed the process"
    print pid.pid, pid.returncode

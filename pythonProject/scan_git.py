import subprocess
import shutil
import re
import os, stat


def scan_log(git_clone_url = "https://github.com/fredricklitvin/leaked_password_test.git"):
     subprocess.run(["cmd","/c","git","clone",git_clone_url,"test_project"], text= True, check= True, capture_output= True)
     git_log_check = subprocess.run(["cmd","/c","git","log","-p"], text= True, check= True, capture_output= True, cwd="./test_project")
     # print(git_log_check.stdout)
     with open("regex_checker.txt") as f:
        for x in f:
            if ":" not in x:
                continue
            first_part, second_part = x.split(":",1)
            second_part = second_part.split("\n")
            for line in git_log_check.stdout.splitlines():
                if re.search(second_part[0], line, re.IGNORECASE):
                    found_secrets.append(line)

def force_remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


if __name__ == "__main__":
    found_secrets = []

    scan_log()
    for things in found_secrets:
        print(things)


    shutil.rmtree('./test_project', onerror=force_remove_readonly)



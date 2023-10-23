#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import yaml

ART_CONTAINER_NAME = "dockerbadboy/art:latest"

REPLAY_EXT = ".scap"
TEST_EXT = ".yaml"

RULES_FILENAME = "rules.txt"
RULES_FALCO = "/etc/falco/falco_rules.yaml"

MAX_RETRIES = 3

EXPECTED = 0
HIT = 1
DELIM = "=" * 50
NEED_REPLAYS=True
summary = {}
falco_rules = {}

container_id = ""

def parse_falco_rules(filepath):
    if not os.path.isfile(filepath):
        print(f"{filepath} files doesn't exist")
        exit(420)
        return

    with open(filepath, "r") as f:
        try:
            parsed = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)

    for p in parsed:
        if p.get("rule", False):
            try:
                falco_rules[p["rule"]] = p["output"].split("%")[0].split(" (")[0]
            except Exception as e:
                continue

def print_summary():
    print()
    print("=" * 50)
    print("Summary")
    print("=" * 50)

    print("Tests that hit all expected rules:")
    for key in summary:
        if len(summary[key][EXPECTED]) == len(summary[key][HIT]) and len(summary[key][HIT]) > 0:
            print(f"{key} ({len(summary[key][HIT])}/{len(summary[key][EXPECTED])})")

    print("\nOthers:")
    for key in summary:
        if len(summary[key][EXPECTED]) != len(summary[key][HIT]):
            print(f"{key} ({len(summary[key][HIT])}/{len(summary[key][EXPECTED])}), unhit rules: {summary[key][EXPECTED]}")
    print(f"\n{DELIM}\ntests with no hits and no expected hits (need to write rules.txt or verify fileparse):")
    for key in summary:
        if len(summary[key][EXPECTED]) == len(summary[key][HIT]) and len(summary[key][HIT]) == 0 and len(summary[key][EXPECTED]) == 0:
            print(f"{key} ({len(summary[key][HIT])}/{len(summary[key][EXPECTED])})")

def parse_expected(test_name, lines):
    summary[test_name] = [[], []]

    if len(falco_rules) == 0:
        return 0

    for rule_name in lines:
        if rule_name in falco_rules:
            summary[test_name][EXPECTED].append(falco_rules[rule_name])

    return len(summary[test_name][EXPECTED])

def kill_container(container_id):
    out = subprocess.check_output("docker ps", shell=True, text=True)
    if ART_CONTAINER_NAME in out:
                print(f"\nKilling {ART_CONTAINER_NAME} container...")
                result = subprocess.run(["docker", "kill", container_id], capture_output=True, text=True)
                if result.stdout.strip() != container_id:
                    if ("not running" in result.stdout or "not running" in result.stderr):
                        print("done.")
                    else:    
                        print(f"Failed to kill {ART_CONTAINER_NAME} container")
    subprocess.run("sudo killall sysdig falco", shell=True)

def do_filter(func, values):
    try:
        return next(filter(func, values))
    except StopIteration:
        return None

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def start_container(container_name):
    # some tests need --privileged flag
    result = subprocess.run(["docker", "run", "--privileged", "-d", container_name, "sleep", "1000"], capture_output=True, text=True)
    return result.returncode, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def make_all_replays():
    global container_id

    dirs = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, d))]
    scaps = []
    for dir in dirs:
        test_name = os.path.split(dir)[-1]

        # find test yaml file
        yaml = do_filter(lambda v: True if v == test_name + TEST_EXT else False, os.listdir(dir))
        if yaml == None:
            print(f"Couldn't find {test_name}/{test_name + TEST_EXT}, skipping")
            continue

        # check if .scap replay file already exists for current test
        scap = do_filter(lambda v: True if v.endswith(REPLAY_EXT) else False, os.listdir(dir))
        if scap != None:
            print(f"Replay file ({os.path.abspath(scap)}) for {test_name} already found, skipping")
            continue

        # check if rules.txt file exists
        rules = do_filter(lambda v: True if v == RULES_FILENAME else False, os.listdir(dir))
        if rules == None:
            print(f"Couldn't find {RULES_FILENAME} file for {test_name}, skipping")
            continue

        rules = os.path.join(dir, rules)
        with open(rules, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        if parse_expected(test_name, lines) == 0:
            continue

        expect = summary[test_name][EXPECTED]

        print(f"{DELIM}\nRunning {yaml}...")

        scap = os.path.join(dir, test_name + REPLAY_EXT)
        scaps.append(scap)
        sysdig_proc = subprocess.Popen(["sudo", "-S", "sysdig", "-w", scap], stdout=subprocess.DEVNULL)

        curr = 0
        while curr < MAX_RETRIES:
            result = subprocess.run(["docker", "exec", container_id, "pwsh", "-Command", f"Import-Module \"~/AtomicRedTeam/invoke-atomicredteam/Invoke-AtomicRedTeam.psd1\" -Force; Invoke-AtomicTest {test_name} -GetPreReqs; Invoke-AtomicTest {test_name}; Invoke-AtomicTest {test_name} -CleanUp"], capture_output=True, text=True)
            if result.returncode == 0:
                break

            print("docker exec failed, output:")
            print(result.stdout, result.stderr)

            out = subprocess.check_output("docker ps", shell=True, text=True)
            if ART_CONTAINER_NAME not in out:
                print(f"Starting {ART_CONTAINER_NAME} container ({curr + 1}/{MAX_RETRIES} retries)...")
                ret, container_id = start_container(ART_CONTAINER_NAME)
                if ret != 0:
                    print("Failed:")
                    print(container_id)
                    exit(1)
                print(f"Done, container id: {container_id}")
                curr += 1
            else:
                print(f"docker exec command failed but {ART_CONTAINER_NAME} is running?")
                kill_container(container_id)
                exit(1)

        print(escape_ansi(result.stdout))
        sysdig_proc.kill()
    return dirs

def run_loop():
    if NEED_REPLAYS:
        dirs = make_all_replays()
    else:
        dirs = [os.path.join(dirpath, d) for d in os.listdir(dirpath) if os.path.isdir(os.path.join(dirpath, d))]
    
    #check falco results
    for dir in dirs:
        test_name = os.path.split(dir)[-1]
        scap = os.path.join(dir, test_name + REPLAY_EXT)

        # check if rules.txt file exists
        rules = do_filter(lambda v: True if v == RULES_FILENAME else False, os.listdir(dir))
        if rules == None:
            print(f"Couldn't find {RULES_FILENAME} file for {test_name}, skipping")
            continue
        rules = os.path.join(dir, rules)
        with open(rules, "r") as f:
            lines = [line.strip() for line in f.readlines()]
        if parse_expected(test_name, lines) == 0:
            continue

        expect = summary[test_name][EXPECTED]
        print(f"{DELIM}\n {test_name} {scap} {expect}")
        print(f"Expecting {len(expect)} rule hits: {expect}\n{DELIM}")

        # verify if the target falco rule has been hit
        result = subprocess.run(f'docker run --rm -i --privileged -v /var/run/docker.sock:/host/var/run/docker.sock \
            -v /proc:/host/proc:ro \
            -v /lib/modules:/host/lib/modules:ro \
            -v /usr:/host/usr:ro \
            -v /etc:/host/etc:ro \
            -v /etc/falco:/etc/falco \
             -v {os.path.abspath(scap)}:/home/scap  andreater/falco-modern-x86:latest falco -e /home/scap -r {RULES_FALCO}', capture_output=True, text=True, shell=True)
        lines = result.stdout.split("\n")
        if result.returncode != 0:
            print(f"{DELIM}\n {result.stderr} \n{DELIM}")
        print(f"looking for {expect} in {lines} ({result})")
        for e in expect:
            for line in lines:
                # reached end falco rule outputs
                if "Events detected: " in line:
                    break
                elif e in line:
                    summary[test_name][HIT].append(f"\"{e}\": {line}")
                    break

     
        print(f"{DELIM}\nRule hits: {len(summary[test_name][HIT])}/{len(expect)}")
        for hit in summary[test_name][HIT]:
            print(hit)
        print(DELIM)

def main():
    global container_id, falco_rules

    print("Starting ART docker container... ", end="", flush=True)
    ret, container_id = start_container(ART_CONTAINER_NAME)
    if ret != 0:
        print("Failed:")
        print(container_id)
        exit(1)
    print(f"Done, container id: {container_id}\n")

    print(f"Parsing {RULES_FALCO} file... ", end="", flush=True)
    parse_falco_rules(RULES_FALCO)
    if len(falco_rules) == 0:
        print("Failed")
    else:
        print(f"Done, parsed {len(falco_rules)} rules")

    try:
        run_loop()
    except KeyboardInterrupt:
        print("\nStopping...")

    if container_id != "":
        kill_container(container_id)

    print_summary()

if len(sys.argv) < 2:
    print(f"{sys.argv[0]} <DIR>")
    exit(1)
# if len(sys.argv) > 2:
#     for arg in sys.argv:
#         if "make-replays" in arg or "make_replays" in arg:
#             NEED_REPLAYS=True


dirpath = os.path.normpath(os.path.join(os.getcwd(), sys.argv[1]))
print(f"Executing in: {dirpath}")
main()
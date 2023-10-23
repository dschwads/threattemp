from typing import Tuple
import click
import subprocess

@click.group()
def cli():
    pass



@cli.command()
@click.option("--local-ip", default="127.0.0.1", help="local ip that docker can reach to deploy log4j exploit")
def do_log4j(local_ip):
    """runs a log4j demo scenario locally via Docker."""
    subprocess.call(("bash do_log4j_nohands.sh " + local_ip).split(" "))

@cli.command()
@click.option("--mode", default="docker", help="Choose from 'docker'(local docker), 'k8s', or 'fargate'")
@click.option("--test", "-t", multiple=True, default=[], help="choose one or a subset of tests to run. Defaults to all tests.")
def do_atomicred(mode, test: Tuple):
    """Runs atomic red team tests on a local or remote environment in order to trigger Sysdig Secure events."""
    if mode == "docker":
        subprocess.call(("docker run dockerbadboy/art pwsh RunTests.ps1 " + " ".join(test)).split(" "))
    elif mode == "k8s":
        print("please wait")
        pass
    elif mode == "fargate":
        print("KEKW")
        subprocess.call("docker run dockerbadboy/stg-client terraform apply -auto-approve")
        pass



if __name__ == "__main__":
    cli()

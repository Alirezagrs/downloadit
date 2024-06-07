import argparse

from aiodownloader.models.app_model import read

parser = argparse.ArgumentParser()

parser.add_argument(
    "--show-status",
    help="show the status of your downloads",
)
args = parser.parse_args()

if args:
    read()

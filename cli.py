import argparse

from models.app_model import read

parser = argparse.ArgumentParser()

parser.add_argument(
    "--show_status",
    help="show the status of your downloads",
)
args = parser.parse_args()

if args:
    read()

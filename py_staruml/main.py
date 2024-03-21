import argparse
import os
from py_staruml import StarUML

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description='PyStarUML')

    # Add the generateproject argument
    parser.add_argument('--generateproject', metavar='P', type=str, help='Generate a Django project from a .mdj file')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call your functions or modules based on the command-line arguments
    if args.generateproject:
        # Create a StarUML object
        staruml = StarUML(args.generateproject)

        # Generate the Django project
        staruml.generate_django_project()

if __name__ == '__main__':
    main()
import sys
import subprocess
import pkg_resources
import os

def check_and_install_libraries():
    # Get the path to the requirements.txt file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_path = os.path.join(current_dir, 'requirements.txt')

    print(f"Checking requirements from: {requirements_path}")

    # Read the requirements
    with open(requirements_path, 'r') as f:
        requirements = f.read().splitlines()

    # Check if all requirements are satisfied
    missing = []
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
            print(f"Requirement satisfied: {requirement}")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"Requirement missing or outdated: {requirement}")
            missing.append(requirement)

    if missing:
        print("Some required libraries are missing or need updating. Attempting to install/update...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])
            print("All required libraries have been successfully installed/updated.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install/update required libraries automatically. Error: {str(e)}")
            print("Please install/update the following libraries manually:")
            for lib in missing:
                print(f"- {lib}")
            print("\nTo install/update manually, follow these steps:")
            print("1. Open a command prompt or terminal")
            print("2. Navigate to the project directory")
            print("3. Run the following command:")
            print(f"   {sys.executable} -m pip install --upgrade -r {requirements_path}")
            print("\nIf you continue to experience issues, please refer to the project documentation or contact support.")
            sys.exit(1)
    else:
        print("All required libraries are already installed and up to date.")

if __name__ == "__main__":
    check_and_install_libraries()
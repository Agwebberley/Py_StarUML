import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEBUG = True

if DEBUG:
    logger.setLevel(logging.DEBUG)

def load_elements(json_path):
    """Load elements data from a JSON file."""
    try:
        with open(json_path, "r") as file:
            elements = json.load(file)
            logger.debug("Elements loaded from JSON file.")
            return elements
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        return []

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.debug(f"Directory created: {directory_path}")
    except Exception as e:
        logger.error(f"Error creating directory: {e}")

def function_exists(file_path, function_name):
    """Check if a function already exists in a file."""
    if not os.path.exists(file_path):
        # Create file if it doesn't exist and add import statements
        with open(file_path, "w") as f:
            f.write("from prefect import task\n\n")
        return False
    with open(file_path, "r") as f:
        content = f.read()
        return f"def {function_name}(" in content

def create_functions(elements, directory):
    """Create functions in respective files based on prototype."""
    for element in elements:
        file_path = os.path.join(directory, f"{element['prototype']}.py")
        function_name = f"element_{element['id']}"
        if not function_exists(file_path, function_name):
            try:
                with open(file_path, "a") as f:
                    f.write(f"@task\ndef {function_name}(*args, **kwargs):\n")
                    f.write(f"    name = \"{element['name']}\"\n")
                    f.write(f"    # Add your code here\n\n")
                logger.debug(f"Function {function_name} added to {file_path}")
            except Exception as e:
                logger.error(f"Error writing to file {file_path}: {e}")

def main():
    elements_file_path = "elements.json"
    elements_dir = "elements"

    elements = load_elements(elements_file_path)
    if not elements:
        logger.error("No elements to process.")
        return

    create_directory(elements_dir)
    create_functions(elements, elements_dir)
    logger.info("Script completed successfully.")

if __name__ == "__main__":
    main()

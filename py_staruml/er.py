import json
import os
import logging


class StarUML:
    """
    Represents a StarUML object that provides functionality to load and manipulate StarUML data.

    Attributes:
        file_path (str): The path to the StarUML file.
        folder_path (str): The path to the folder where the generated Django models will be saved.
        data (dict): The loaded StarUML data.

    Methods:
        __init__(self, file_path, folder_path=''): Initializes a new instance of the StarUML class.
        load_data(self): Loads the StarUML data from the file.
        pretty_print(self, data): Prints the StarUML data in a pretty format.
        iterate_elements(self, element=None, predicate=None): Iterates over the elements in the StarUML data.
        get_app_names(self): Returns a list of unique app names in the StarUML data.
        print_out(self): Prints the table and relationship information from the StarUML data.
        generate_django_models(self): Generates Django models based on the StarUML data.
        database_dictionary(self): Converts the StarUML data into a dictionary representing the database structure.
        create_database_structure(self, element, sub_element): Creates the database structure for a given element and sub-element.
        add_columns(self, sub_element, app_name, table_name): Adds columns to the database structure for a given sub-element.
        add_relationships(self, sub_element, element, app_name, table_name): Adds relationships to the database structure for a given sub-element.
        remove_relationship_attributes(self): Removes relationship attributes from the database structure.
        get_columns(self, table_info, type_mapping): Returns the column definitions for a given table.
        get_relationships(self, table_info, app_name): Returns the relationship definitions for a given table.
        get_relationships_imports(self): Returns a dictionary with the app name as the key and the set of imported tables as the value.
        get_empty_classes(self): Returns a dictionary with the app name as the key and the set of empty classes as the value.
    """

    def __init__(self, file_path, folder_path=''):
        self.file_path = file_path
        self.database = {}
        self.data = None
        if folder_path == '':
            folder_path = file_path.split('.')[0]
        self.folder_path = folder_path


    def load_data(self):
        try:
            with open(self.file_path) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            logging.error(f"Error: File '{self.file_path}' not found.")
        except json.JSONDecodeError:
            logging.error(f"Error: Invalid JSON format in file '{self.file_path}'.")
    
    def dump_database_to_file(self, dir_path='', file_path=''):
        """
        Dump the database to a JSON file.

        Args:
            file_path (str): The path to the file where the database will be dumped.
            dir_path (str): The path to the directory where the file will be saved.

        Returns:
            None
        """
        try:
            if file_path == '':
                file_path = self.file_path.split('.')[0] + '_database.json'
            if not file_path.endswith('.json'):
                file_path += '.json'
                logging.warning(f"File path does not end with '.json'. Appending '.json' to the file path: {file_path}")
            if os.path.exists(file_path):
                logging.warning(f"File '{file_path}' already exists. It will be overwritten.")
            if self.database is {}:
                self.database_dictionary()
                logging.warning("Database is empty. Generating database dictionary.")
            if dir_path != '':
                file_path = os.path.join(dir_path, os.path.basename(file_path))
                logging.warning(f"Directory path provided. File path updated to: {file_path}")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logging.debug(f"Dumping database to file: {file_path}")
            with open(file_path, 'w') as file:
                json.dump(self.database, file)
        except IOError as e:
            logging.error(f"Error dumping database to file: {e}")
        logging.info(f"Database dumped to file: {file_path}")

    def pretty_print(self, data):
            """
            Prints the given data in a pretty format.

            Args:
                data: The data to be printed.

            Raises:
                TypeError: If the data cannot be pretty printed.

            """
            if data is None:
                data = self.data
            try:
                logging.info(json.dumps(data, indent=4))
            except TypeError:
                logging.error("Error: Unable to pretty print the data.")

    def iterate_elements(self, element=None, predicate=None):
        """
        Iterates over the elements in the data structure.

        Args:
            element (dict): The element to start iterating from. If None, the root element will be used.
            predicate (function): A function that takes an element as input and returns a boolean value. Only elements
                                  for which the predicate returns True will be yielded.

        Yields:
            dict: The next element in the iteration.

        Raises:
            KeyError: If the data format is invalid.

        Returns:
            None
        """
        if element is None:
            element = self.data
        try:
            for sub_element in element['ownedElements']:
                if predicate is None or predicate(sub_element):
                    yield sub_element
                if 'ownedElements' in sub_element:
                    for sub_sub_element in self.iterate_elements(sub_element, predicate):
                        yield sub_sub_element
        except KeyError:
            logging.error("Error: Invalid data format.")

    def get_app_names(self):
            """
            Returns a list of unique application names extracted from the elements.

            Returns:
                list: A list of unique application names.

            Raises:
                KeyError: If the data format is invalid.
            """
            try:
                return list(set(sub_element['name'].split('.')[0] for sub_element in self.iterate_elements()))
            except KeyError:
                logging.error("Error: Invalid data format.")
                return []

    def generate_django_models(self):
        """
        Generates Django models based on the database dictionary.

        This method iterates over the database dictionary and generates Django models
        for each table in the database. It uses a type mapping dictionary to map
        database column types to Django field types. It also handles relationships
        between tables and imports related models if necessary.

        Returns:
            None

        Raises:
            IOError: If there is an error writing the generated models to a file.
        """
        type_mapping = {
            'CHAR': 'CharField',
            'INTEGER': 'IntegerField',
            'FLOAT': 'FloatField',
            'BOOLEAN': 'BooleanField',
            'DATE': 'DateField',
            'DATETIME': 'DateTimeField',
            'TEXT': 'TextField',
            'VARCHAR': 'CharField'
        }
        database = self.database_dictionary()
        relationships_imports = self.get_relationships_imports()
        file_contents = {}

        for app_name, tables in database.items():
            app_folder = os.path.join(self.folder_path, app_name)
            os.makedirs(app_folder, exist_ok=True)

            if app_folder not in file_contents:
                file_contents[app_folder] = f"from django.db import models\n"
                if relationships_imports is not None and app_name in relationships_imports:
                    for table_name, connected_tables in relationships_imports[app_name].items():
                        for connected_app, connected_table in connected_tables:
                            file_contents[app_folder] += f"from {connected_app}.models import {connected_table}\n"

            for table_name, table_info in tables.items():
                file_contents[app_folder] += f"\n\nclass {table_name}(models.Model):\n"
                file_contents[app_folder] += self.get_columns(table_info, type_mapping)
                file_contents[app_folder] += self.get_relationships(table_info, app_name)
                if not table_info['columns'] and not table_info['relationships']:
                    file_contents[app_folder] += "    pass\n"

        for app_folder, content in file_contents.items():
            try:
                with open(os.path.join(app_folder, 'models.py'), 'w') as f:
                    f.write(content)
                    logging.info(f"Generated Django models for app: {app_folder}")
            except IOError as e:
                logging.error(f"Error writing file: {e}")

    def get_columns(self, table_info, type_mapping):
        """
        Generate Django model columns based on the provided table_info and type_mapping.

        Args:
            table_info (dict): Information about the table, including its columns.
            type_mapping (dict): Mapping of column types from the original database to Django model field types.

        Returns:
            str: Generated Django model columns.

        Raises:
            Exception: If there is an error processing a column.

        """
        columns = ""
        if 'columns' in table_info:
            for column in table_info['columns']:
                try:
                    column_name, column_attributes = list(column.items())[0]
                    column_type, column_length, column_primary_key, column_unique, column_not_null = column_attributes
                    django_column_type = type_mapping.get(column_type, 'CharField')
                    columns += f"    {column_name} = models.{django_column_type}("
                    if django_column_type == 'CharField':
                        if not column_length:
                            column_length = 255
                        columns += f"max_length={column_length}, "
                    if column_primary_key:
                        columns += "primary_key=True, "
                    if column_unique:
                        columns += "unique=True, "
                    if column_not_null:
                        columns += "null=False, "
                    columns = columns.rstrip(", ")  # Remove trailing comma and whitespace
                    columns += ")\n"
                except Exception as e:
                    logging.error(f"Error: Unable to process column. {e}")
        return columns

    def get_relationships(self, table_info, app_name):
        """
        Retrieves the relationships for a given table and app name.

        Args:
            table_info (dict): A dictionary containing information about the table.
            app_name (str): The name of the Django app.

        Returns:
            str: A string representation of the relationships.

        Raises:
            Exception: If there is an error processing the relationship.

        """
        relationships = ""
        if 'relationships' in table_info:
            for relationship in table_info['relationships']:
                try:
                    relationship_name = list(relationship.keys())[0]
                    connected_app, connected_table, cardinality = list(relationship.values())[0]
                    model_type = 'ForeignKey' if cardinality == '0..*' else 'OneToOneField'
                    if connected_app == app_name:
                        relationships += f"    {relationship_name} = models.{model_type}('{connected_table}', on_delete=models.CASCADE)\n"
                    else:
                        relationships += f"    {relationship_name} = models.{model_type}({connected_table}, on_delete=models.CASCADE)\n"
                except Exception as e:
                    logging.error(f"Error: Unable to process relationship. {e}")
        return relationships

    def get_relationships_imports(self):
        """
        Return a dictionary with the app name as the key and the set of imported tables as the value.

        Returns:
            dict: A dictionary containing the app name as the key and the set of imported tables as the value.
                  The imported tables are represented as a set of tuples, where each tuple contains the name of the
                  connected app and the name of the connected table.
        """
        relationships_imports = {}
        try:
            database = self.database_dictionary()
            for app_name, tables in database.items():
                relationships_imports[app_name] = {}
                for table_name, table_info in tables.items():
                    relationships_imports[app_name][table_name] = set()
                    for relationship in table_info['relationships']:
                        try:
                            connected_app, connected_table, _ = list(relationship.values())[0]
                            if connected_app != app_name:
                                relationships_imports[app_name][table_name].add((connected_app, connected_table))
                        except (KeyError, IndexError):
                            logging.error("Error: Invalid relationship format.")
        except KeyError:
            logging.error("Error: Invalid data format.")
        return relationships_imports

    def get_empty_classes(self):
        """
        Returns a dictionary with the app name as the key and the set of empty classes as the value.

        The method iterates over the elements and checks if they are of type 'ERDEntity'. If an element is found
        to be an 'ERDEntity' and does not have any 'columns' attribute, it extracts the app name and table name
        from the element's name and adds the table name to the set of empty classes under the corresponding app name.

        Returns:
            A dictionary with the app name as the key and the set of empty classes as the value.

        Raises:
            KeyError: If the data format is invalid.
        """
        empty_classes = {}
        try:
            for sub_element in self.iterate_elements(predicate=lambda x: x['_type'] == 'ERDEntity'):
                if 'columns' not in sub_element:
                    try:
                        app_name, table_name = sub_element['name'].split('.')
                        if app_name not in empty_classes:
                            empty_classes[app_name] = set()
                        empty_classes[app_name].add(table_name)
                    except (KeyError, ValueError):
                        logging.error("Error: Invalid entity format.")
        except KeyError:
            logging.error("Error: Invalid data format.")
        return empty_classes
    
    def database_dictionary(self):
        """
        Creates a dictionary representing the database structure.

        This method iterates through the elements of an ERDDataModel and creates a dictionary
        that represents the structure of the database. It adds tables, columns, and relationships
        to the dictionary based on the elements in the ERDDataModel.

        Returns:
            dict: A dictionary representing the database structure.

        Raises:
            Exception: If an error occurs while creating the database dictionary.
        """
        logging.info("Creating database dictionary...")
        self.database = {}
        try:
            for element in self.iterate_elements(predicate=lambda x: x['_type'] == 'ERDDataModel'):
                for sub_element in self.iterate_elements(element, predicate=lambda x: x['_type'] == 'ERDEntity'):
                    self.create_database_structure(element, sub_element)
                    app_name, table_name = sub_element['name'].split('.')
                    if 'columns' in sub_element:
                        self.add_columns(sub_element, app_name, table_name)
                    if 'ownedElements' in sub_element:
                        self.add_relationships(sub_element, element, app_name, table_name)
            self.remove_relationship_attributes()
            logging.info("Database dictionary created.")
        except Exception as e:
            logging.error(f"Error creating database dictionary: {e}")
        return self.database
    
    def create_database_structure(self, element, sub_element):
        """
        Creates the database structure for the given element and sub_element.

        Args:
            element (str): The element to create the database structure for.
            sub_element (dict): The sub-element containing the name of the app and table.

        Returns:
            None
        """
        app_name, table_name = sub_element['name'].split('.')
        if app_name not in self.database:
            self.database[app_name] = {}
        if table_name not in self.database[app_name]:
            self.database[app_name][table_name] = {'columns': [], 'relationships': []}

    def add_columns(self, sub_element, app_name, table_name):
        """
        Adds columns to a table in the database.

        Args:
            sub_element (dict): The sub-element containing the column information.
            app_name (str): The name of the application.
            table_name (str): The name of the table.

        Returns:
            None

        Raises:
            KeyError: If the column format is invalid.
            ValueError: If the length value is invalid.
            Exception: If an error occurs while adding columns.
        """
        for column in sub_element['columns']:
            try:
                column_info = {
                    column['name']: [
                        column['type'],
                        int(column.get('length', 0)),
                        bool(column.get('primaryKey', False)),
                        bool(column.get('unique', False)),
                        bool(column.get('notNull', False))
                    ]
                }
                # Ignore primary key columns
                if column_info[column['name']][2]:
                    logging.warning(f"Ignoring primary key column '{column['name']}' in table '{table_name}' of app '{app_name}'.")
                    continue
                # If the column is a text type and has a length of 0, set the length to 255
                if column_info[column['name']][0] in ['CHAR', 'TEXT'] and column_info[column['name']][1] == 0:
                    column_info[column['name']][1] = 255
                    logging.warning(f"Column '{column['name']}' in table '{table_name}' of app '{app_name}' has a length of 0. Setting length to 255.")
                self.database[app_name][table_name]['columns'].append(column_info)
            except KeyError as e:
                logging.error(f"Error: Invalid column format in table '{table_name}' of app '{app_name}'. Skipping column.")
            except ValueError as e:
                logging.error(f"Error: Invalid length value in column '{column['name']}' of table '{table_name}' in app '{app_name}'. Skipping column.")
            except Exception as e:
                logging.error(f"Error: An error occurred while adding column '{column['name']}' to table '{table_name}' in app '{app_name}': {e}. Skipping column.")
    
    def add_relationships(self, sub_element, element, app_name, table_name):
        """
        Adds relationships between tables in the database.

        Args:
            sub_element (dict): The sub-element containing the relationship information.
            element (dict): The element containing the table information.
            app_name (str): The name of the application.
            table_name (str): The name of the table.

        Returns:
            None

        Raises:
            Exception: If an error occurs while adding relationships.

        """
        try:
            for relationship in self.iterate_elements(sub_element, predicate=lambda x: x['_type'] == 'ERDRelationship'):
                connected_table_id = relationship['end2']['reference']['$ref']
                # The connected table is the table that the relationship needs to be added to
                # Which is different from the current table, we need to make sure it exists, if it doesn't, create it
                for connected_element in self.iterate_elements(element, predicate=lambda x: x['_type'] == 'ERDEntity' and x['_id'] == connected_table_id):
                    connected_table_name = connected_element['name']
                    connected_app_name, connected_table_name = connected_table_name.split('.')
                    if connected_app_name not in self.database:
                        self.database[connected_app_name] = {}
                    if connected_table_name not in self.database[connected_app_name]:
                        self.database[connected_app_name][connected_table_name] = {'columns': [], 'relationships': []}
                    # Determine the cardinality of the relationship
                    if 'cardinality' in relationship['end1'] and 'cardinality' in relationship['end2']:
                        cardinality_end1 = relationship['end1']['cardinality']
                        cardinality_end2 = relationship['end2']['cardinality']
                    elif 'cardinality' in relationship['end1']:
                        cardinality_end1 = relationship['end1']['cardinality']
                        cardinality_end2 = "1"
                    else:
                        cardinality_end2 = relationship['end2']['cardinality']
                        cardinality_end1 = "1"

                    if cardinality_end1 == '0..*':
                        # If the cardinality on end1 is 0..*, connect the relationship to the current table
                        self.database[app_name][table_name]['relationships'].append({relationship['name']: [connected_app_name, connected_table_name, cardinality_end1]})

                    if cardinality_end2 == '0..*':
                        # If the cardinality on end2 is 0..*, connect the relationship to the connected table
                        self.database[connected_app_name][connected_table_name]['relationships'].append({relationship['name']: [app_name, table_name, cardinality_end2]})

                    if (cardinality_end1 == '1' or cardinality_end1 =="0..1") and (cardinality_end2 == '1' or cardinality_end2 == "0..1"):
                        # If the cardinality on both ends is 1, connect the relationship to the current table
                        # Because there is no way to determine which table is the parent, we will ask the user to specify

                        # Search both tables to see if one of them has a column that has the same name as the relationship
                        # If it does, that table is the child
                        # If neither table has a column with the same name as the relationship, ask the user to specify
                        child_table = None
                        child_app = None
                        parent_table = None
                        parent_app = None

                        # Search the first table
                        if app_name in self.database and table_name in self.database[app_name]:
                            table_info = self.database[app_name][table_name]
                            if relationship['name'] in [list(column.keys())[0] for column in table_info['columns']]:
                                child_table = table_name
                                child_app = app_name
                                parent_table = connected_table_name
                                parent_app = connected_app_name

                        # Search the second table
                        if connected_app_name in self.database and connected_table_name in self.database[connected_app_name]:
                            table_info = self.database[connected_app_name][connected_table_name]
                            if relationship['name'] in [list(column.keys())[0] for column in table_info['columns']]:
                                child_table = connected_table_name
                                child_app = connected_app_name
                                parent_table = table_name
                                parent_app = app_name
                        else:
                            # If the relationship is not found in either table, assume the parent is the current table
                            child_table = table_name
                            child_app = app_name
                            parent_table = connected_table_name
                            parent_app = connected_app_name
                            logging.warning(f"Unable to determine parent and child tables for relationship '{relationship['name']}'. Please specify the parent table.")

                        self.database[child_app][child_table]['relationships'].append({relationship['name']: [parent_app, parent_table, cardinality_end1]})
        except Exception as e:
            logging.error(f"An error occurred while adding relationships: {str(e)}")
    def remove_relationship_attributes(self):
        """
        Removes duplicate relationship attributes from the database tables.

        This method iterates over the database tables and removes any relationship attributes
        from the columns list of each table. It logs the details of the removed attributes.

        Raises:
            KeyError: If the data format is invalid.
            Exception: If an error occurs while removing relationship attributes.

        """
        try:
            for app_name, tables in self.database.items():
                for table_name, table_info in tables.items():
                    for relationship in table_info['relationships']:
                        relationship_name = list(relationship.keys())[0]
                        self.database[app_name][table_name]['columns'] = [column for column in table_info['columns'] if list(column.keys())[0] != relationship_name]
                        logging.info(f"Removed relationship attribute '{relationship_name}' from table '{table_name}' in app '{app_name}'.")
        except KeyError as e:
            logging.error(f"Error: Invalid data format. {e}")
        except Exception as e:
            logging.error(f"Error: An error occurred while removing relationship attributes: {e}")

if __name__ == '__main__':
    LOGGING_LEVEL = logging.DEBUG
    LOGGING_FORMAT = '%(levelname)s - %(message)s'
    LOGGING_FILE = 'app.log'
    LOGGING_MODE = 'w'
    logging.basicConfig(filename=LOGGING_FILE, filemode=LOGGING_MODE, format=LOGGING_FORMAT, level=LOGGING_LEVEL)
    file_paths = ['Database.mdj', 'DBProject.mdj', 'Prototype.mdj']
    for i in file_paths:
        staruml = StarUML(i)
        staruml.load_data()
        staruml.database_dictionary()
        staruml.dump_database_to_file(dir_path='schemas')
        staruml.generate_django_models()
        logging.info(f"Database dictionary for file '{i}': {staruml.database}")
        logging.info(f"Empty classes for file '{i}': {staruml.get_empty_classes()}")
        logging.info(f"App names for file '{i}': {staruml.get_app_names()}")
        logging.info(f"Relationships imports for file '{i}': {staruml.get_relationships_imports()}")
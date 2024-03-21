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
        __init__(file_path, folder_path=''): Initializes a new instance of the StarUML class.
        load_data(): Loads the StarUML data from the file.
        pretty_print(data): Prints the StarUML data in a pretty format.
        iterate_elements(element=None, predicate=None): Iterates over the elements in the StarUML data.
        get_app_names(): Returns a list of unique app names in the StarUML data.
        print_out(): Prints the table and relationship information from the StarUML data.
        generate_django_models(): Generates Django models based on the StarUML data.
        database_dictionary(): Converts the StarUML data into a dictionary representing the database structure.
    """

    def __init__(self, file_path, folder_path=''):
        self.file_path = file_path
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

    def pretty_print(self, data):
        if data is None:
            data = self.data
        try:
            logging.info(json.dumps(data, indent=4))
        except TypeError:
            logging.error("Error: Unable to pretty print the data.")

    def iterate_elements(self, element=None, predicate=None):
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
        try:
            return list(set(sub_element['name'].split('.')[0] for sub_element in self.iterate_elements()))
        except KeyError:
            logging.error("Error: Invalid data format.")
            return []
    def print_out(self):
        def get_table_info(sub_element):
            output = []
            if sub_element['_type'] == 'ERDEntity':  # Exclude relationships from being treated as tables
                output.append('Table: ' + sub_element['name'])
                output.append('Columns:')
                if 'columns' in sub_element:
                    for column in sub_element['columns']:
                        output.append(' - ' + column['name'] + ': ' + column['type'])
                        if 'tags' in column:
                            output.append('    Tags:')
                            for tag in column['tags']:
                                output.append('     - ' + tag['name'] + ': ' + tag['value'])

                output.append('Relationships:')
                if 'ownedElements' in sub_element:
                    for relationship in sub_element['ownedElements']:
                        if relationship['_type'] == 'ERDRelationship':
                            output.append(' - ' + relationship['name'] + '; connected Table: ' + relationship['end2']['reference']['$ref'])
                            for connected_element in self.data['ownedElements']:
                                if connected_element['_type'] == 'ERDEntity' and connected_element['_id'] == relationship['end2']['reference']['$ref']:
                                    output.append(sub_element['name'] + ' - ' + connected_element['name'] + '; Cardinality: ' +
                                                  (relationship['end1']['cardinality'] if 'cardinality' in relationship['end1'] else '1') +
                                                  '-' +
                                                  (relationship['end2']['cardinality'] if 'cardinality' in relationship['end2'] else '1'))

            return '\n'.join(output)
        
        output = [get_table_info(sub_element) for sub_element in self.iterate_elements()]
        print('\n'.join(output))

    def generate_django_models(self):
        type_mapping = {
            'CHAR': 'CharField',
            'INTEGER': 'IntegerField',
            'FLOAT': 'FloatField',
            'BOOLEAN': 'BooleanField',
            'DATE': 'DateField',
            'DATETIME': 'DateTimeField',
            'TEXT': 'TextField',
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
                            file_contents[app_folder] += f"from {connected_app} import {connected_table}\n"

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
        columns = ""
        if 'columns' in table_info:
            for column in table_info['columns']:
                try:
                    column_name, column_attributes = list(column.items())[0]
                    column_type, column_length, column_primary_key, column_unique, column_not_null = column_attributes
                    django_column_type = type_mapping.get(column_type, 'CharField')
                    columns += f"    {column_name} = models.{django_column_type}("
                    if column_type in ['CHAR', 'TEXT'] and column_length > 0:
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
        # Return a dictionary with the app name as the key and the set of imported tables as the value
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
        # Return a dictionary with the app name as the key and the set of empty classes as the value
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
        app_name, table_name = sub_element['name'].split('.')
        if app_name not in self.database:
            self.database[app_name] = {}
        if table_name not in self.database[app_name]:
            self.database[app_name][table_name] = {'columns': [], 'relationships': []}

    def add_columns(self, sub_element, app_name, table_name):
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
    # Note: Path may need to be changed to the location of the Database.mdj file
    logging.basicConfig(filename='app.log', filemode='w', format='%(levelname)s - %(message)s', level=logging.INFO)
    file_path = 'Database.mdj'
    erd = StarUML(file_path)
    erd.load_data()
    #erd.print_out()
    erd.generate_django_models()
    dbproject = "DBProject.mdj"
    erd = StarUML(dbproject)
    erd.load_data()
    #erd.print_out()
    erd.generate_django_models()

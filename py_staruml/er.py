import json
import os
import sqlite3
import ast

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
        cfv = ClassFunctionVisitor()
        self.cfv = cfv

    # Rest of the code...
class StarUML:
    """
    TODO: Add a validation function to check if the models already match the database design
    TODO: Allow any functions within models.py files to persist
    """
    def __init__(self, file_path, folder_path=''):
        self.file_path = file_path
        self.data = None
        if folder_path == '':
            folder_path = file_path.split('.')[0]
        self.folder_path = folder_path
        cfv = ClassFunctionVisitor()
        self.cfv = cfv


    def load_data(self):
        with open(self.file_path) as f:
            self.data = json.load(f)

    def pretty_print(self, data):
        if data is None:
            data = self.data
        print(json.dumps(data, indent=4))
    
    def iterate_elements(self, element=None, predicate=None):
        if element is None:
            element = self.data
        for sub_element in element['ownedElements']:
            if predicate is None or predicate(sub_element):
                yield sub_element
            if 'ownedElements' in sub_element:
                for sub_sub_element in self.iterate_elements(sub_element, predicate):
                    yield sub_sub_element
    
    def get_app_names(self):
        return list(set(sub_element['name'].split('.')[0] for sub_element in self.iterate_elements()))
    
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
            with open(os.path.join(app_folder, 'models.py'), 'w') as f:
                f.write(content)

    def get_columns(self, table_info, type_mapping):
        columns = ""
        if 'columns' in table_info:
            for column in table_info['columns']:
                # The column is a dictionary with the key being the column name and the value being a list of attributes
                column_name = list(column.keys())[0]
                column_type = column[column_name][0]
                column_length = column[column_name][1]
                column_primary_key = column[column_name][2]
                column_unique = column[column_name][3]
                column_not_null = column[column_name][4]
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
        return columns

    def get_relationships(self, table_info, app_name):
        relationships = ""
        if 'relationships' in table_info:
            for relationship in table_info['relationships']:
                relationship_name = list(relationship.keys())[0]
                connected_app, connected_table, cardinality = list(relationship.values())[0]
                model_type = 'ForeignKey' if cardinality == '0..*' else 'OneToOneField'
                if connected_app == app_name:
                    relationships += f"    {relationship_name} = models.{model_type}('{connected_table}', on_delete=models.CASCADE)\n"
                else:
                    relationships += f"    {relationship_name} = models.{model_type}({connected_table}, on_delete=models.CASCADE)\n"
        return relationships

    def database_dictionary(self):
        # As an intermediate step, create a dictionary of the database structure
        """ Structure: 
        {app_name: 
            {table_name: 
                {columns: [{column_name: [{attribute_name: attribute_value}...]}], 
                relationships: [{relationship_name: [connected_app, connected_table, cardinality]}]
        }}}
        """
        database = {}
        for element in self.iterate_elements(predicate=lambda x: x['_type'] == 'ERDDataModel'):
            for sub_element in self.iterate_elements(element, predicate=lambda x: x['_type'] == 'ERDEntity'):
                app_name, table_name = sub_element['name'].split('.')
                if app_name not in database:
                    database[app_name] = {}
                if table_name not in database[app_name]:
                    database[app_name][table_name] = {'columns': [], 'relationships': []}
                if 'columns' in sub_element:
                    if 'columns' not in database[app_name][table_name]:
                        database[app_name][table_name]['columns'] = []
                    for column in sub_element['columns']:
                        column_info = {
                            column['name']: [
                                column['type'],
                                int(column.get('length', 0)),
                                bool(column.get('primaryKey', False)),
                                bool(column.get('unique', False)),
                                bool(column.get('notNull', False))
                            ]
                        }
                        database[app_name][table_name]['columns'].append(column_info)
                        
                if 'ownedElements' in sub_element:
                    for relationship in self.iterate_elements(sub_element, predicate=lambda x: x['_type'] == 'ERDRelationship'):
                        connected_table_id = relationship['end2']['reference']['$ref']
                        # The connected table is the table that the relationship needs to be added to
                        # Which is different from the current table, we need to make sure it exists, if it doesn't, create it
                        for connected_element in self.iterate_elements(element, predicate=lambda x: x['_type'] == 'ERDEntity' and x['_id'] == connected_table_id):
                            connected_table_name = connected_element['name']
                            connected_app_name, connected_table_name = connected_table_name.split('.')
                            if connected_app_name not in database:
                                database[connected_app_name] = {}
                            if connected_table_name not in database[connected_app_name]:
                                database[connected_app_name][connected_table_name] = {'columns': [], 'relationships': []}
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
                                database[app_name][table_name]['relationships'].append({relationship['name']: [connected_app_name, connected_table_name, cardinality_end1]})
                            
                            if cardinality_end2 == '0..*':
                                # If the cardinality on end2 is 0..*, connect the relationship to the connected table
                                database[connected_app_name][connected_table_name]['relationships'].append({relationship['name']: [app_name, table_name, cardinality_end2]})
                            
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
                                if app_name in database and table_name in database[app_name]:
                                    table_info = database[app_name][table_name]
                                    if relationship['name'] in [list(column.keys())[0] for column in table_info['columns']]:
                                        child_table = table_name
                                        child_app = app_name
                                        parent_table = connected_table_name
                                        parent_app = connected_app_name

                                # Search the second table
                                if connected_app_name in database and connected_table_name in database[connected_app_name]:
                                    table_info = database[connected_app_name][connected_table_name]
                                    if relationship['name'] in [list(column.keys())[0] for column in table_info['columns']]:
                                        child_table = connected_table_name
                                        child_app = connected_app_name
                                        parent_table = table_name
                                        parent_app = app_name

                                if child_table is None or child_app is None or parent_table is None or parent_app is None:
                                    child_table = input(f"Which table is the child in the relationship {relationship['name']} between 1. {app_name}.{table_name} and 2. {connected_app_name}.{connected_table_name}? ")
                                    if child_table == "1":
                                        child_table = table_name
                                        child_app = app_name
                                        parent_table = connected_table_name
                                        parent_app = connected_app_name
                                    else:
                                        child_table = connected_table_name
                                        child_app = connected_app_name
                                        parent_table = table_name
                                        parent_app = app_name

                                database[child_app][child_table]['relationships'].append({relationship['name']: [parent_app, parent_table, cardinality_end1]})
        # Remove attributes that correspond to relationships
        for app_name, tables in database.items():
            for table_name, table_info in tables.items():
                for relationship in table_info['relationships']:
                    relationship_name = list(relationship.keys())[0]
                    database[app_name][table_name]['columns'] = [column for column in table_info['columns'] if list(column.keys())[0] != relationship_name]
        return database

    def get_relationships_imports(self):
        # Return a dictionary with the app name as the key and the set of imported tables as the value
        relationships_imports = {}
        database = self.database_dictionary()
        for app_name, tables in database.items():
            relationships_imports[app_name] = {}
            for table_name, table_info in tables.items():
                relationships_imports[app_name][table_name] = set()
                for relationship in table_info['relationships']:
                    connected_app, connected_table, _ = list(relationship.values())[0]
                    if connected_app != app_name:
                        relationships_imports[app_name][table_name].add((connected_app, connected_table))
        return relationships_imports

    def get_empty_classes(self):
        # Return a dictionary with the app name as the key and the set of empty classes as the value
        empty_classes = {}

        for sub_element in self.iterate_elements(predicate=lambda x: x['_type'] == 'ERDEntity'):
            if 'columns' not in sub_element:
                app_name, table_name = sub_element['name'].split('.')
                if app_name not in empty_classes:
                    empty_classes[app_name] = set()
                empty_classes[app_name].add(table_name)
        return empty_classes

if __name__ == '__main__':
    # Note: Path may need to be changed to the location of the Database.mdj file
    DBG = True
    file_path = 'Database.mdj'
    erd = StarUML(file_path)
    erd.load_data()
    erd.print_out()
    erd.generate_django_models()
    if DBG: erd.pretty_print(erd.database_dictionary())
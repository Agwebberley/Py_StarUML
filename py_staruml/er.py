import json
import os
import logging


class StarUML:
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
        try:
            if file_path == '':
                file_path = self.file_path.split('.')[0] + '_database.json'
            if not file_path.endswith('.json'):
                file_path += '.json'
                logging.warning(f"File path does not end with '.json'. Appending '.json' to the file path: {file_path}")
            if os.path.exists(file_path):
                logging.warning(f"File '{file_path}' already exists. It will be overwritten.")
            if self.database == {}:
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

    def pretty_print(self, data=None):
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

    def generate_django_models(self):
        type_mapping = {
            'CHAR': 'CharField',
            'Decimal': 'DecimalField',
            'INTEGER': 'IntegerField',
            'FLOAT': 'FloatField',
            'BOOLEAN': 'BooleanField',
            'DATE': 'DateField',
            'DATETIME': 'DateTimeField',
            'TEXT': 'TextField',
            'VARCHAR': 'CharField'
        }
        database = self.database_dictionary()
        file_content = "from django.db import models\n\n"
        graphene_content = "import graphene\nfrom graphene_django.types import DjangoObjectType\n\nclass Query(graphene.ObjectType):\n"

        for table_name, table_info in database.items():
            file_content += f"\n\nclass {table_name.capitalize()}(models.Model):\n"
            file_content += self.get_columns(table_info, type_mapping)
            file_content += self.get_relationships(table_info)
            if not table_info['columns'] and not table_info['relationships']:
                file_content += "    pass\n"

            graphene_content = self.generate_graphql_schema()

        app_folder = os.path.join(self.folder_path, 'app')
        os.makedirs(app_folder, exist_ok=True)

        try:
            with open(os.path.join(app_folder, 'models.py'), 'w') as f:
                f.write(file_content)
                logging.info(f"Generated Django models for app: {app_folder}")
            with open(os.path.join(app_folder, 'schema.py'), 'w') as f:
                f.write(graphene_content)
                logging.info(f"Generated GraphQL schema for app: {app_folder}")
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

    def get_relationships(self, table_info):
        relationships = ""
        if 'relationships' in table_info:
            for relationship in table_info['relationships']:
                try:
                    relationship_name = list(relationship.keys())[0]
                    connected_table, cardinality = list(relationship.values())[0]
                    model_type = 'ForeignKey' if cardinality == '0..*' else 'OneToOneField'
                    relationships += f"    {relationship_name} = models.{model_type}('{connected_table.capitalize()}', on_delete=models.CASCADE)\n"
                except Exception as e:
                    logging.error(f"Error: Unable to process relationship. {e}")
        return relationships

    def generate_graphene_type(self, table_name):
        return f"\n\nclass {table_name.capitalize()}Type(DjangoObjectType):\n    class Meta:\n        model = {table_name.capitalize()}\n\n"

    def generate_graphene_query(self, table_name):
        query_str = f"    all_{table_name}s = graphene.List({table_name.capitalize()}Type)\n"
        query_str += f"    def resolve_all_{table_name}s(self, info, **kwargs):\n"
        query_str += f"        return {table_name.capitalize()}.objects.all()\n\n"
        return query_str
    
    def generate_graphene_imports(self, table_names):
        imports_str = "import graphene\nfrom graphene_django.types import DjangoObjectType\nfrom app.models import " + ", ".join([name.capitalize() for name in table_names]) + "\n\n"
        return imports_str

    def generate_graphql_schema(self):
        database = self.database_dictionary()
        table_names = list(database.keys())

        imports_str = self.generate_graphene_imports(table_names)
        types_str = "".join([self.generate_graphene_type(name) for name in table_names])
        queries_str = "class Query(graphene.ObjectType):\n" + "".join([self.generate_graphene_query(name) for name in table_names])

        return imports_str + types_str + queries_str


    def get_relationships_imports(self):
        relationships_imports = {}
        try:
            database = self.database_dictionary()
            for table_name, table_info in database.items():
                relationships_imports[table_name] = set()
                for relationship in table_info['relationships']:
                    try:
                        connected_table = list(relationship.values())[0][1]
                        relationships_imports[table_name].add(connected_table)
                    except (KeyError, IndexError):
                        logging.error("Error: Invalid relationship format.")
        except KeyError:
            logging.error("Error: Invalid data format.")
        return relationships_imports

    def get_empty_classes(self):
        empty_classes = set()
        try:
            for sub_element in self.iterate_elements(predicate=lambda x: x['_type'] == 'ERDEntity'):
                if 'columns' not in sub_element:
                    try:
                        table_name = sub_element['name']
                        empty_classes.add(table_name)
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
                    table_name = sub_element['name']
                    if 'columns' in sub_element:
                        self.add_columns(sub_element, table_name)
                    if 'ownedElements' in sub_element:
                        self.add_relationships(sub_element, element, table_name)
            self.remove_relationship_attributes()
            logging.info("Database dictionary created.")
        except Exception as e:
            logging.error(f"Error creating database dictionary: {e}")
        return self.database
    
    def create_database_structure(self, element, sub_element):
        table_name = sub_element['name']
        if table_name not in self.database:
            self.database[table_name] = {'columns': [], 'relationships': []}

    def add_columns(self, sub_element, table_name):
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
                if column_info[column['name']][2]:
                    logging.warning(f"Ignoring primary key column '{column['name']}' in table '{table_name}'.")
                    continue
                if column_info[column['name']][0] in ['CHAR', 'TEXT'] and column_info[column['name']][1] == 0:
                    column_info[column['name']][1] = 255
                    logging.warning(f"Column '{column['name']}' in table '{table_name}' has a length of 0. Setting length to 255.")
                self.database[table_name]['columns'].append(column_info)
            except KeyError as e:
                logging.error(f"Error: Invalid column format in table '{table_name}'. Skipping column.")
            except ValueError as e:
                logging.error(f"Error: Invalid length value in column '{column['name']}' of table '{table_name}'. Skipping column.")
            except Exception as e:
                logging.error(f"Error: An error occurred while adding column '{column['name']}' to table '{table_name}': {e}. Skipping column.")
    
    def add_relationships(self, sub_element, element, table_name):
        try:
            for relationship in self.iterate_elements(sub_element, predicate=lambda x: x['_type'] == 'ERDRelationship'):
                connected_table_id = relationship['end2']['reference']['$ref']
                for connected_element in self.iterate_elements(element, predicate=lambda x: x['_type'] == 'ERDEntity' and x['_id'] == connected_table_id):
                    connected_table_name = connected_element['name']
                    if connected_table_name not in self.database:
                        self.database[connected_table_name] = {'columns': [], 'relationships': []}
                    cardinality_end1 = relationship['end1'].get('cardinality', '1')
                    cardinality_end2 = relationship['end2'].get('cardinality', '1')
                    if cardinality_end1 == '0..*':
                        self.database[table_name]['relationships'].append({relationship['name']: [connected_table_name, cardinality_end1]})
                    if cardinality_end2 == '0..*':
                        self.database[connected_table_name]['relationships'].append({relationship['name']: [table_name, cardinality_end2]})
                    if (cardinality_end1 == '1' or cardinality_end1 == "0..1") and (cardinality_end2 == '1' or cardinality_end2 == "0..1"):
                        self.database[table_name]['relationships'].append({relationship['name']: [connected_table_name, cardinality_end1, cardinality_end2]})  # Add the missing second value to the relationship dictionary
        except Exception as e:
            logging.error(f"An error occurred while adding relationships: {str(e)}")

    def remove_relationship_attributes(self):
        try:
            for table_name, table_info in self.database.items():
                for relationship in table_info['relationships']:
                    relationship_name = list(relationship.keys())[0]
                    self.database[table_name]['columns'] = [column for column in table_info['columns'] if list(column.keys())[0] != relationship_name]
                    logging.info(f"Removed relationship attribute '{relationship_name}' from table '{table_name}'.")
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
    file_paths = ['order_manager.mdj']
    for i in file_paths:
        staruml = StarUML(i)
        staruml.load_data()
        staruml.database_dictionary()
        staruml.dump_database_to_file(dir_path='schemas')
        staruml.generate_django_models()
        logging.info(f"Database dictionary for file '{i}': {staruml.database}")
        logging.info(f"Empty classes for file '{i}': {staruml.get_empty_classes()}")
        logging.info(f"Relationships imports for file '{i}': {staruml.get_relationships_imports()}")

import json
import os
import logging

class BPMN:
    """
    This class is used to read BPMN (StarUML json) files and convert them to python prefect flows
    """
    def __init__(self, file_path):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info('BPMN object created')
        self.file_path = file_path
        self.data = None
        self.load_data()
        self.pretty_print()

    def load_data(self):
        try:
            with open(self.file_path) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            logging.error(f"Error: File '{self.file_path}' not found.")
        except json.JSONDecodeError:
            logging.error(f"Error: Invalid JSON format in file '{self.file_path}'.")
    
    def pretty_print(self):
        """ Print the BPMN data in the format:
        Element Type : Element Name

        """
        for process in self.data['ownedElements']:
            for element in process['ownedElements']:
                if element['_type'] == 'BPMNStartEvent':
                    self.pretty_print_recursive(element)
    
    def pretty_print_recursive(self, element):
        print(f"{element['_type']} : {element['name']}")
        if 'ownedElements' in element:
            for sqf in element['ownedElements']:
                reference = sqf['target']['$ref']
                for process in self.data['ownedElements']:
                    for element in process['ownedElements']:
                        if element['_id'] == reference:
                            self.pretty_print_recursive(element)
    
    def get_start_event(self, bpmn_data):
        """
        Get the start event from the BPMN data
        """
        for element in bpmn_data['ownedElements']:
            if element['_type'] == 'BPMNStartEvent':
                return element
        return None


if __name__ == '__main__':
    bpmn = BPMN("bpmnTEST.mdj")
    print(bpmn.get_start_event(bpmn.data))
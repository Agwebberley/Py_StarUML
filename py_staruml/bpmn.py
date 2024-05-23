import json
import argparse
import logging
from typing import List, Dict, Tuple, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BPMNToPrefectConverter:
    def __init__(self, json_file: str, output_file: str, debug: bool = False):
        self.json_file = json_file
        self.output_file = output_file
        if debug:
            logger.setLevel(logging.DEBUG)

    def load_bpmn_json(self) -> Dict[str, Any]:
        try:
            with open(self.json_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading JSON file: {e}")
            raise

    def parse_elements(self, bpmn_data: Dict[str, Any]) -> Tuple[Dict[str, str], Dict[str, List[str]], List[Dict[str, str]]]:
        elements = bpmn_data['ownedElements'][0]['ownedElements']
        task_mapping = {}
        prototype_mapping = {}
        sequence_flows = []

        for element in elements:
            element_id = element['_id']
            element_name_id = element.get('id', element_id)
            element_type = element['_type']
            if element_type in ['BPMNStartEvent', 'BPMNTask', 'BPMNEndEvent', 'BPMNExclusiveGateway']:
                task_name = f"element_{element_name_id}"
                task_mapping[element_id] = task_name
                if element_type not in prototype_mapping:
                    prototype_mapping[element_type] = []
                prototype_mapping[element_type].append(task_name)
            if 'ownedElements' in element:
                for sub_element in element['ownedElements']:
                    if sub_element['_type'] == 'BPMNSequenceFlow':
                        sequence_flows.append({
                            'source': sub_element['source']['$ref'],
                            'target': sub_element['target']['$ref'],
                            'name': sub_element.get('name', None)
                        })
                        logger.debug(f"Found sequence flow: {sub_element['source']['$ref']} -> {sub_element['target']['$ref']} with condition: {sub_element.get('name', None)}")

        return task_mapping, prototype_mapping, sequence_flows

    def build_execution_graph(self, sequence_flows: List[Dict[str, str]]) -> Tuple[Dict[str, List[Tuple[str, str]]], Dict[str, List[str]]]:
        graph = {}
        merge_points = {}
        for flow in sequence_flows:
            source = flow['source']
            target = flow['target']
            condition = flow.get('name')
            if source not in graph:
                graph[source] = []
            graph[source].append((target, condition))
            if target not in merge_points:
                merge_points[target] = []
            merge_points[target].append(source)
            logger.debug(f"Adding to graph: {source} -> {target} with condition: {condition}")
        return graph, merge_points

    def generate_prefect_flow(self, task_mapping: Dict[str, str], prototype_mapping: Dict[str, List[str]], execution_graph: Dict[str, List[Tuple[str, str]]], merge_points: Dict[str, List[str]], execution_order: List[str]) -> None:
        with open(self.output_file, 'w') as f:
            self.write_imports(f, prototype_mapping)
            f.write("\n@flow(name='bpmn_to_prefect')\n")
            f.write("def bpmn_flow():\n")
            self.write_task_calls(f, task_mapping, execution_graph, merge_points, execution_order, 1)
            f.write("\nif __name__ == '__main__':\n")
            f.write("    bpmn_flow()\n")

    def write_imports(self, f, prototype_mapping: Dict[str, List[str]]) -> None:
        f.write("from prefect import flow, task\n")
        for prototype, tasks in prototype_mapping.items():
            task_imports = ", ".join(tasks)
            f.write(f"from elements.{prototype} import {task_imports}\n")
            logger.debug(f"Importing {tasks} from elements.{prototype}")

    def write_task_calls(self, f, task_mapping: Dict[str, str], execution_graph: Dict[str, List[Tuple[str, str]]], merge_points: Dict[str, List[str]], execution_order: List[str], indent: int) -> None:
        visited = set()

        def write_tasks(source, indent):
            if source in visited:
                return
            visited.add(source)

            if source not in task_mapping:
                return

            element_type = self.get_element_type(source)
            indent_str = ' ' * indent * 4

            if 'Gateway' in element_type:
                f.write(f"{indent_str}result = {task_mapping[source]}()\n")
                logger.debug(f"Handling gateway with id: {source}")
                for target, condition in execution_graph[source]:
                    if condition is not None:
                        f.write(f"{indent_str}if result == '{condition}':\n")
                        write_tasks(target, indent + 1)
                    else:
                        f.write(f"{indent_str}else:\n")
                        write_tasks(target, indent + 1)
            elif source in merge_points:
                logger.debug(f"Handling merge point with id: {source}")
                for target in merge_points[source]:
                    if target in execution_graph:
                        for t, _ in execution_graph[target]:
                            if t not in visited:
                                f.write(f"{indent_str}{task_mapping[t]}()\n")
                f.write(f"{indent_str}{task_mapping[source]}()\n")
            else:
                f.write(f"{indent_str}{task_mapping[source]}()\n")
                if source in execution_graph:
                    for target, _ in execution_graph[source]:
                        write_tasks(target, indent)

        for source in execution_order:
            write_tasks(source, indent)

    def get_element_type(self, element_id: str) -> str:
        elements = self.bpmn_data['ownedElements'][0]['ownedElements']
        for element in elements:
            if element['_id'] == element_id:
                return element['_type']
        return ""

    def convert(self):
        self.bpmn_data = self.load_bpmn_json()
        task_mapping, prototype_mapping, sequence_flows = self.parse_elements(self.bpmn_data)
        execution_graph, merge_points = self.build_execution_graph(sequence_flows)
        execution_order = self.topological_sort(execution_graph)
        logger.debug(f"Execution graph: {execution_graph}")
        logger.debug(f"Execution order: {execution_order}")
        self.generate_prefect_flow(task_mapping, prototype_mapping, execution_graph, merge_points, execution_order)

    def topological_sort(self, graph: Dict[str, List[Tuple[str, str]]]) -> List[str]:
        visited = set()
        order = []

        def dfs(node):
            if node in visited:
                return
            visited.add(node)
            if node in graph:
                for neighbor, _ in graph[node]:
                    dfs(neighbor)
            order.append(node)

        for node in graph:
            dfs(node)
        
        order.reverse()
        return order

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert BPMN JSON to Prefect Flow Python script')
    parser.add_argument('json_file', type=str, help='Path to the BPMN JSON file')
    parser.add_argument('output_file', type=str, help='Path to the output Python file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()
    converter = BPMNToPrefectConverter(args.json_file, args.output_file, debug=args.debug)
    converter.convert()

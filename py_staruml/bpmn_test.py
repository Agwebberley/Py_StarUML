import unittest
from unittest.mock import patch, mock_open
import json
from bpmn import BPMNToPrefectConverter

class TestBPMNToPrefectConverter(unittest.TestCase):
    
    def setUp(self):
        self.converter = BPMNToPrefectConverter('dummy.json', 'output.py')
        self.mock_bpmn_data = {
            "ownedElements": [{
                "ownedElements": [
                    {
                        "_id": "1",
                        "_type": "BPMNStartEvent",
                        "id": "StartEvent_1",
                        "ownedElements": [
                            {
                                "_id": "5",
                                "_type": "BPMNSequenceFlow",
                                "source": {"$ref": "1"},
                                "target": {"$ref": "2"},
                                "name": None
                            }
                        ]
                    },
                    {
                        "_id": "2",
                        "_type": "BPMNTask",
                        "id": "Task_1",
                        "ownedElements": [
                            {
                                "_id": "6",
                                "_type": "BPMNSequenceFlow",
                                "source": {"$ref": "2"},
                                "target": {"$ref": "3"},
                                "name": None
                            }
                        ]
                    },
                    {
                        "_id": "3",
                        "_type": "BPMNExclusiveGateway",
                        "id": "Gateway_1",
                        "ownedElements": [
                            {
                                "_id": "7",
                                "_type": "BPMNSequenceFlow",
                                "source": {"$ref": "3"},
                                "target": {"$ref": "4"},
                                "name": "True"
                            }
                        ]
                    },
                    {
                        "_id": "4",
                        "_type": "BPMNEndEvent",
                        "id": "EndEvent_1",
                        "ownedElements": []
                    }
                ]
            }]
        }

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "ownedElements": [{
            "ownedElements": [
                {
                    "_id": "1",
                    "_type": "BPMNStartEvent",
                    "id": "StartEvent_1",
                    "ownedElements": [
                        {
                            "_id": "5",
                            "_type": "BPMNSequenceFlow",
                            "source": {"$ref": "1"},
                            "target": {"$ref": "2"},
                            "name": None
                        }
                    ]
                },
                {
                    "_id": "2",
                    "_type": "BPMNTask",
                    "id": "Task_1",
                    "ownedElements": [
                        {
                            "_id": "6",
                            "_type": "BPMNSequenceFlow",
                            "source": {"$ref": "2"},
                            "target": {"$ref": "3"},
                            "name": None
                        }
                    ]
                },
                {
                    "_id": "3",
                    "_type": "BPMNExclusiveGateway",
                    "id": "Gateway_1",
                    "ownedElements": [
                        {
                            "_id": "7",
                            "_type": "BPMNSequenceFlow",
                            "source": {"$ref": "3"},
                            "target": {"$ref": "4"},
                            "name": "True"
                        }
                    ]
                },
                {
                    "_id": "4",
                    "_type": "BPMNEndEvent",
                    "id": "EndEvent_1",
                    "ownedElements": []
                }
            ]
        }]
    }))
    def test_load_bpmn_json(self, mock_file):
        data = self.converter.load_bpmn_json()
        self.assertEqual(data, self.mock_bpmn_data)
        mock_file.assert_called_with('dummy.json')

    def test_parse_elements(self):
        self.converter.bpmn_data = self.mock_bpmn_data
        task_mapping, prototype_mapping, sequence_flows = self.converter.parse_elements(self.mock_bpmn_data)
        
        expected_task_mapping = {
            "1": "element_StartEvent_1",
            "2": "element_Task_1",
            "3": "element_Gateway_1",
            "4": "element_EndEvent_1"
        }
        
        expected_prototype_mapping = {
            "BPMNStartEvent": ["element_StartEvent_1"],
            "BPMNTask": ["element_Task_1"],
            "BPMNExclusiveGateway": ["element_Gateway_1"],
            "BPMNEndEvent": ["element_EndEvent_1"]
        }
        
        expected_sequence_flows = [
            {"source": "1", "target": "2", "name": None},
            {"source": "2", "target": "3", "name": None},
            {"source": "3", "target": "4", "name": "True"}
        ]
        
        self.assertEqual(task_mapping, expected_task_mapping)
        self.assertEqual(prototype_mapping, expected_prototype_mapping)
        self.assertEqual(sequence_flows, expected_sequence_flows)
    
    def test_build_execution_graph(self):
        sequence_flows = [
            {"source": "1", "target": "2", "name": None},
            {"source": "2", "target": "3", "name": None},
            {"source": "3", "target": "4", "name": "True"}
        ]
        expected_graph = {
            "1": [("2", None)],
            "2": [("3", None)],
            "3": [("4", "True")]
        }
        graph = self.converter.build_execution_graph(sequence_flows)
        self.assertEqual(graph, expected_graph)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_prefect_flow(self, mock_file):
        self.converter.bpmn_data = self.mock_bpmn_data  # Ensure bpmn_data is set
        task_mapping = {
            "1": "element_StartEvent_1",
            "2": "element_Task_1",
            "3": "element_Gateway_1",
            "4": "element_EndEvent_1"
        }
        prototype_mapping = {
            "BPMNStartEvent": ["element_StartEvent_1"],
            "BPMNTask": ["element_Task_1"],
            "BPMNExclusiveGateway": ["element_Gateway_1"],
            "BPMNEndEvent": ["element_EndEvent_1"]
        }
        execution_graph = {
            "1": [("2", None)],
            "2": [("3", None)],
            "3": [("4", "True")]
        }
        execution_order = ["1", "2", "3", "4"]
        
        self.converter.generate_prefect_flow(task_mapping, prototype_mapping, execution_graph, execution_order)
        
        expected_calls = [
            unittest.mock.call("from prefect import flow, task\n"),
            unittest.mock.call("from elements.BPMNStartEvent import element_StartEvent_1\n"),
            unittest.mock.call("from elements.BPMNTask import element_Task_1\n"),
            unittest.mock.call("from elements.BPMNExclusiveGateway import element_Gateway_1\n"),
            unittest.mock.call("from elements.BPMNEndEvent import element_EndEvent_1\n"),
            unittest.mock.call("\n@flow(name='bpmn_to_prefect')\n"),
            unittest.mock.call("def bpmn_flow():\n"),
            unittest.mock.call("    element_StartEvent_1()\n"),
            unittest.mock.call("    element_Task_1()\n"),
            unittest.mock.call("    result = element_Gateway_1()\n"),
            unittest.mock.call("    if result == 'True':\n"),
            unittest.mock.call("        element_EndEvent_1()\n"),
            unittest.mock.call("\nif __name__ == '__main__':\n"),
            unittest.mock.call("    bpmn_flow()\n")
        ]

        mock_file().write.assert_has_calls(expected_calls, any_order=True)

if __name__ == '__main__':
    unittest.main()

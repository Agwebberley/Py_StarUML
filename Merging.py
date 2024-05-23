from prefect import flow, task
from elements.BPMNStartEvent import element_1
from elements.BPMNExclusiveGateway import element_20
from elements.BPMNTask import element_29, element_30
from elements.BPMNEndEvent import element_41

@flow(name='bpmn_to_prefect')
def bpmn_flow():
    element_1()
    result = element_20()
    if result == 'FAIL':
        element_30()
        element_29()
    if result == 'SUCCESS':
        element_30()
    element_41()

if __name__ == '__main__':
    bpmn_flow()

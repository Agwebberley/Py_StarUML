from prefect import flow, task
from elements.BPMNStartEvent import element_36
from elements.BPMNExclusiveGateway import element_43
from elements.BPMNEndEvent import element_39, element_46
from elements.BPMNTask import element_40

@flow(name='bpmn_to_prefect')
def bpmn_flow():
    element_36()
    result = element_43()
    if result == 'False':
        element_40()
        element_39()
    if result == 'True':
        element_40()
        element_46()

if __name__ == '__main__':
    bpmn_flow()

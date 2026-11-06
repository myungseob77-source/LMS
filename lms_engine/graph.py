from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from .harness import Harness
from .loop import initial_state, execute_step, verify_step

class State(TypedDict):
    task: str
    max_attempts: int
    attempts: int
    output: str
    error: str
    status: str


def build_graph(harness: Harness):
    graph = StateGraph(State)
    graph.add_node('plan', lambda state: {'status': 'pending'})
    graph.add_node('execute', lambda state: execute_step(harness, state))
    graph.add_node('verify', lambda state: verify_step(harness, state))
    graph.add_edge(START, 'plan')
    graph.add_edge('plan', 'execute')
    graph.add_edge('execute', 'verify')
    graph.add_conditional_edges('verify',
        lambda state: 'execute' if state['status'] == 'retry' else END,
        ['execute', END])
    return graph.compile()


def run_graph(harness: Harness, task: str, max_attempts: int = 3) -> dict:
    state = initial_state(task, max_attempts)
    return build_graph(harness).invoke(state, {'recursion_limit': 2 * max_attempts + 5})

from .harness import Harness


def initial_state(task: str, max_attempts: int) -> dict:
    if not task.strip():
        raise ValueError("task must not be empty")
    if isinstance(max_attempts, bool) or not 1 <= max_attempts <= 100:
        raise ValueError("max_attempts must be between 1 and 100")
    return dict(task=task, max_attempts=max_attempts, attempts=0,
                output="", error="", status="pending")


def execute_step(harness: Harness, state: dict) -> dict:
    attempt = state['attempts'] + 1
    try:
        output = harness.execute(state['task'], attempt)
        return dict(attempts=attempt, output=output, error="")
    except Exception as exc:
        # Persist the exception type only; provider errors may contain credentials.
        return dict(attempts=attempt, output="", error=type(exc).__name__)


def verify_step(harness: Harness, state: dict) -> dict:
    error = state['error']
    try:
        valid = not error and bool(harness.verify(state['output']))
    except Exception as exc:
        valid, error = False, type(exc).__name__
    status = 'success' if valid else (
        'failed' if state['attempts'] >= state['max_attempts'] else 'retry')
    return dict(status=status, error=error)


def run_loop(harness: Harness, task: str, max_attempts: int = 3) -> dict:
    state = initial_state(task, max_attempts)
    while state['status'] not in ('success', 'failed'):
        state.update(execute_step(harness, state))
        state.update(verify_step(harness, state))
    return state

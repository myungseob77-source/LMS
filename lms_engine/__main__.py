import argparse
import json
from pathlib import Path
from uuid import uuid4
from .harness import Harness
from .loop import run_loop


def main():
    parser = argparse.ArgumentParser(description='LMS harness / loop / graph demo')
    parser.add_argument('--mode', choices=['loop', 'graph'], default='graph')
    parser.add_argument('--task', default='Verify the LMS development environment')
    parser.add_argument('--max-attempts', type=int, default=3)
    parser.add_argument('--log-dir', type=Path, default=Path('.runs'))
    parser.add_argument('--diagram', action='store_true')
    args = parser.parse_args()
    if args.diagram:
        from .graph import build_graph
        print(build_graph(Harness.demo()).get_graph().draw_mermaid())
        return
    runner = run_loop
    if args.mode == 'graph':
        from .graph import run_graph
        runner = run_graph
    try:
        result = runner(Harness.demo(), args.task, args.max_attempts)
    except ValueError as exc:
        parser.error(str(exc))
    args.log_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    (args.log_dir / f'{uuid4().hex}.json').write_text(payload, encoding='utf-8')
    print(payload)
    raise SystemExit(0 if result['status'] == 'success' else 1)

if __name__ == '__main__':
    main()

"""Shared CLI, exit status and bounded thread runner for explicit acceptance checks."""
import argparse
from pathlib import Path
import threading
import time


def output_directory(description, name, restart=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parents[2] / "output" / "validation" / name)
    if restart:
        parser.add_argument("--restart", action="store_true")
    return parser.parse_args()


def suite_exit_code(results):
    outcomes = {r["outcome"] for r in results}
    return 1 if "Fail" in outcomes else 2 if "Blocked" in outcomes else 0


def run_concurrently(functions, describe_error, timeout=15):
    """Abort a stuck test rather than leave a process waiting indefinitely."""
    results = [None] * len(functions)
    barrier = threading.Barrier(len(functions))

    def run(index, function):
        try:
            barrier.wait(timeout=timeout)
            function()
            results[index] = "ok"
        except Exception as error:
            results[index] = describe_error(error)

    threads = [threading.Thread(target=run, args=(i, f), daemon=True)
               for i, f in enumerate(functions)]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    for thread in threads:
        thread.join(max(0, deadline - time.monotonic()))
    if any(thread.is_alive() for thread in threads):
        raise TimeoutError("Concurrent validation exceeded its deadline; stop and inspect the disposable instance.")
    return results

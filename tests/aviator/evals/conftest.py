"""pytest configuration for the AC eval suite.

Mirrors mergeit's tests/codemod/evals/conftest.py, minus the sandbox and
Claude-CLI-version matrix that this plugin doesn't need.
"""

from __future__ import annotations

import time

import pytest
from dotenv import load_dotenv

from . import metrics
from .metrics import color, print_line

# Load .env from the repo root (or any ancestor) so tests can pick up
# ANTHROPIC_API_KEY without the user having to export it in every shell.
load_dotenv()

DEFAULT_EVAL_RUNS = 3
DEFAULT_EVAL_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Markers & CLI
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "eval: mark test as an eval (skipped by default; requires "
        "--run-evals / --run-evals-quick / --run-evals-deep and ANTHROPIC_API_KEY)",
    )
    metrics.verbose = config.option.verbose > 0


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-evals",
        action="store_true",
        default=False,
        help="run all eval tests",
    )
    parser.addoption(
        "--run-evals-quick",
        action="store_true",
        default=False,
        help="run only quick eval tests (deep=False)",
    )
    parser.addoption(
        "--run-evals-deep",
        action="store_true",
        default=False,
        help="run only deep eval tests (deep=True)",
    )
    parser.addoption(
        "--eval-runs",
        type=int,
        default=None,
        help=f"override number of consistency runs (default: {DEFAULT_EVAL_RUNS})",
    )
    parser.addoption(
        "--eval-model",
        type=str,
        default=None,
        help=f"generation model to test (default: {DEFAULT_EVAL_MODEL})",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--run-evals"):
        return

    run_quick = config.getoption("--run-evals-quick")
    run_deep = config.getoption("--run-evals-deep")

    if run_quick or run_deep:
        skip_marker = pytest.mark.skip(reason="not selected by eval filter")
        for item in items:
            if "eval" not in item.keywords:
                continue
            case = getattr(getattr(item, "callspec", None), "params", {}).get("case")
            is_deep = bool(case.deep) if case is not None else False
            if run_quick and is_deep:
                item.add_marker(skip_marker)
            if run_deep and not is_deep:
                item.add_marker(skip_marker)
        return

    skip_eval = pytest.mark.skip(reason="need --run-evals* option to run")
    for item in items:
        if "eval" in item.keywords:
            item.add_marker(skip_eval)


# ---------------------------------------------------------------------------
# Progress hooks
# ---------------------------------------------------------------------------

_eval_start_times: dict[str, float] = {}


def pytest_runtest_setup(item: pytest.Item) -> None:
    if "eval" in item.keywords:
        _eval_start_times[item.nodeid] = time.monotonic()
        print_line(f"\n{color('[EVAL START]', 'cyan')} {item.name}")


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    start = _eval_start_times.pop(report.nodeid, None)
    if start is None:
        return
    elapsed = time.monotonic() - start
    name = report.nodeid.split("::")[-1]
    if report.passed:
        print_line(f"\n{color('[EVAL PASSED]', 'green')} {name} ({elapsed:.1f}s)\n")
    else:
        print_line(f"\n{color('[EVAL FAILED]', 'red')} {name} ({elapsed:.1f}s)\n")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def eval_num_runs(request: pytest.FixtureRequest) -> int:
    n = request.config.getoption("--eval-runs", default=None)
    return n if n is not None else DEFAULT_EVAL_RUNS


@pytest.fixture(scope="session")
def eval_model(request: pytest.FixtureRequest) -> str:
    m = request.config.getoption("--eval-model", default=None)
    return m or DEFAULT_EVAL_MODEL

[private]
default:
    @just --list

[group('evals')]
[doc('Run all AC evals (pass -v for verbose, -k <id> to filter)')]
evals *ARGS:
    uv run pytest tests/aviator/evals/ --run-evals --tb=short --capture=tee-sys {{ARGS}}

[group('evals')]
[doc('Run quick AC evals (deep=False cases only)')]
evals-quick *ARGS:
    uv run pytest tests/aviator/evals/ --run-evals-quick --tb=short --capture=tee-sys {{ARGS}}

[group('evals')]
[doc('Run deep AC evals (deep=True cases only)')]
evals-deep *ARGS:
    uv run pytest tests/aviator/evals/ --run-evals-deep --tb=short --capture=tee-sys {{ARGS}}

[group('evals')]
[doc('Run a single eval case by id, e.g. `just evals-case calculator_bug_fix`')]
evals-case ID *ARGS:
    uv run pytest tests/aviator/evals/ --run-evals -k {{ID}} --tb=short --capture=tee-sys {{ARGS}}

# coding=utf-8


import os
from pathlib import Path

import click

from epab.utils import do


COVERAGE_CONFIG = """
## http://coverage.readthedocs.io/en/latest/config.html
[run]
#timid = True
branch = True
source = epab

[report]
# Regexes for lines to exclude from consideration
exclude_lines =
    # Have to re-enable the standard pragma
    pragma: no cover

    # Don't complain about missing debug-only code:
    def __repr__
    if self\.debug

    # Don't complain if tests don't hit defensive assertion code:
    raise AssertionError
    raise NotImplementedError
    pass

    # Ignore abstract definitions:
    @abc.abstractmethod
    @abc.abstractproperty

    # Don't complain if non-runnable code isn't run:
    if 0:
    if __name__ == .__main__.:

[html]
directory = ./htmlcov
title = Coverage report

[paths]
source=
    ./epab
"""


@click.command()
@click.pass_context
def pytest(ctx):
    """
    Runs Pytest (https://docs.pytest.org/en/latest/)
    """
    os.environ['PYTEST_QT_API'] = 'pyqt5'
    coverage_rc = Path('.coveragerc')
    coverage_rc.write_text(COVERAGE_CONFIG)
    cmd = ['pytest', 'test']
    if os.environ.get('APPVEYOR') and ctx.obj['CONFIG']['test']['av_runner_options']:
        cmd = cmd + ctx.obj['CONFIG']['test']['av_runner']
    elif ctx.obj['CONFIG']['test']['runner_options']:
        cmd = cmd + ctx.obj['CONFIG']['test']['runner_options']
    options = [f'--cov={ctx.obj["CONFIG"]["package"]}', '--cov-report', 'xml', '--cov-report', 'html', '--durations=10',
               '--hypothesis-show-statistics', '--tb=short', '--cov-config', '.coveragerc']
    try:
        do(ctx, cmd + options)
    finally:
        coverage_rc.unlink()
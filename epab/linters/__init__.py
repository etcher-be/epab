# coding=utf-8
"""
Manages linters
"""
import sys
from pathlib import Path

import click

from epab.utils import _info, do, repo_commit, run_once


@run_once
def _pep8(ctx):
    do(ctx, ['autopep8', '-r', '--in-place', '--max-line-length', '120', '.'])


@click.command()
@click.pass_context
def pep8(ctx):
    """
    Runs Pyup's Safety tool (https://pyup.io/safety/)
    """
    _pep8(ctx)


@run_once
def _flake8(ctx):
    ignore = ['--ignore=D203,E126']
    max_line_length = ['--max-line-length=120']
    # noinspection SpellCheckingInspection
    exclude = ['--exclude', '_version.py,_*_version.py,_versioneer.py,versioneer.py,.svn,CVS,.bzr,.hg,.git,'
                            '__pycache__,.tox,__init__.py,dummy_miz.py,build,dist,output,.cache,.hypothesis,'
                            'qt_resource.py,_parking_spots.py,./test/*,./.eggs/*,']
    max_complexity = ['--max-complexity=10']
    do(ctx, ['flake8'] + ignore + max_line_length + exclude + max_complexity)


@click.command()
@click.pass_context
def flake8(ctx):
    """
    Runs Flake8 (http://flake8.pycqa.org/en/latest/)
    """
    _flake8(ctx)


@click.command()
@click.pass_context
def prospector(ctx):
    """
    Runs Landscape.io's Prospector (https://github.com/landscapeio/prospector)

    This includes flake8 & Pylint
    """
    do(ctx, ['prospector'])


@run_once
def _isort(ctx):
    do(ctx, ['isort', '-rc', '-w', '120', '-s', 'versioneer.py', '.'])


@click.command()
@click.pass_context
def isort(ctx):
    """
    Runs iSort (https://pypi.python.org/pypi/isort)
    """
    _isort(ctx)


@run_once
def _pylint(ctx, src, reports):
    # noinspection SpellCheckingInspection
    ignore = ['--ignore=CVS,versioneer.py,_versioneer.py,_version.py',
              '--ignore-patterns=_.*_version']
    line_length = ['--max-line-length=120']
    jobs = ['-j', '2']
    persistent = ['--persistent=y']
    site_packages = str(Path(sys.executable).parent.parent.joinpath(
        'lib/site-packages')).replace('\\', '/')
    init_hook = [f'--init-hook=import sys; sys.path.append("{site_packages}")']
    disable = ['-d', 'disable=logging-format-interpolation,fixme,'
                     'backtick,long-suffix,raw-checker-failed,bad-inline-option,'
                     'locally-disabled,locally-enabled,suppressed-message,'
                     'coerce-method,delslice-method,getslice-method,setslice-method,'
                     'next-method-called,too-many-arguments,too-few-public-methods,'
                     'reload-builtin,oct-method,hex-method,nonzero-method,cmp-method,'
                     'using-cmp-argument,eq-without-hash,exception-message-attribute,sys-max-int,'
                     'bad-python3-import,']
    evaluation = [
        '--evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)']
    output = ['--output-format=text']
    report = ['--reports=n']
    score = ['--score=n']
    if src is None:
        src = ctx.obj['CONFIG']['package']
    cmd = ['pylint', src]
    if reports:
        report = ['--reports=y']
    do(ctx, cmd + ignore + line_length + jobs + persistent + init_hook +
       disable + evaluation + output + report + score)


@click.command()
@click.pass_context
@click.argument('src', type=click.Path(exists=True), default=None, required=False)
@click.option('-r', '--reports', is_flag=True, help='Display full report')
def pylint(ctx, src, reports):
    """
    Analyze a given python SRC (module or package) with Pylint (SRC must exist)

    Default module: CONFIG['package']
    """
    _pylint(ctx, src, reports)


@run_once
def _safety(ctx):
    do(ctx, ['safety', 'check', '--bare'])


@click.command()
@click.pass_context
def safety(ctx):
    """
    Runs Pyup's Safety tool (https://pyup.io/safety/)
    """
    _safety(ctx)


@run_once
def _lint(ctx: click.Context, auto_commit: bool):
    _info('Running all linters')
    ctx.invoke(pep8)
    ctx.invoke(isort)
    ctx.invoke(flake8)
    ctx.invoke(pylint)
    # ctx.invoke(prospector)
    ctx.invoke(safety)
    if auto_commit:
        msg = 'chg: dev: linting [auto]'
        repo_commit(ctx, msg)


@click.command()
@click.pass_context
@click.option('-c', '--auto-commit', is_flag=True, help='Commit the changes')
def lint(ctx: click.Context, auto_commit: bool):
    """
    Runs all linters
    Args:
        ctx: click context
        auto_commit: whether or not to commit results
    """
    _lint(ctx, auto_commit)

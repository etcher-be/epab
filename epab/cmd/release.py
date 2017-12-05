# coding=utf-8
import os
import shutil
import sys
import click
from epab.linters import lint
from epab.utils import _info, bump_version, do, repo_get_current_branch, _error, repo_tag, repo_commit,\
    repo_remove_tag, repo_checkout, repo_merge, repo_push
from epab.cmd import chglog, write_reqs


def _clean(ctx):
    """
    Cleans up build dir
    """
    _info(f'Cleaning project directory...')
    folders_to_cleanup = [
        '.eggs',
        'build',
        f'{ctx.obj["CONFIG"]["package"]}.egg-info',
    ]
    for folder in folders_to_cleanup:
        if os.path.exists(folder):
            _info(f'\tremoving: {folder}')
            shutil.rmtree(folder)


@click.command()
@click.argument('new_version', required=False)
@click.pass_context
def release(ctx, new_version):
    """
    This is meant to be used as a Git pre-push hook
    """
    current_branch = repo_get_current_branch(ctx)
    if current_branch != 'develop':
        _error(f'Cannot release; current branch must be "develop": {current_branch}')
        exit(-1)

    _info('Making new release')

    ctx.invoke(lint)
    repo_commit(ctx, 'chg: dev: linting [auto]')

    write_reqs(ctx)
    repo_commit(ctx, 'chg: dev: update requirements [auto]')

    new_version = bump_version(ctx, new_version)
    _info(f'New version: {new_version}')
    repo_tag(ctx, new_version)
    ctx.invoke(chglog)
    repo_commit(ctx, 'chg: dev: update changelog [auto]')
    repo_remove_tag(ctx, new_version)

    repo_checkout(ctx, 'master')
    repo_merge(ctx, 'develop')
    repo_tag(ctx, new_version)


    _clean(ctx)
    do(ctx, sys.executable.replace('\\', '/') + ' setup.py bdist_wheel')
    do(ctx, 'twine upload dist/* --skip-existing', mute_stdout=True, mute_stderr=True)
    do(ctx, 'pip install -e .')
    _info('All good!')

# coding=utf-8
"""
Manages output functions
"""

import click
import io


def _sanitize(input_: str):
    return input_.encode('ascii', 'ignore').decode()


def _info(txt: str, **args):
    txt = _sanitize(txt)
    click.secho(txt, fg='green', **args)


def _error(txt: str, **args):
    txt = _sanitize(txt)
    click.secho(txt, fg='red', err=True, **args)


def _cmd(txt: str, **args):
    txt = _sanitize(txt)
    click.secho(txt, fg='magenta', **args)


def _out(txt: str, **args):
    txt = _sanitize(txt)
    click.secho(txt, fg='cyan', **args)

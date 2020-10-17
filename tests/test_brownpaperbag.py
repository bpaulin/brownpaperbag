#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `brownpaperbag` package."""

import pytest
from brownpaperbag import brownpaperbag, cli
from click.testing import CliRunner


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0


def test_command_line_sub_interface():
    """Test the CLI."""
    runner = CliRunner()
    env = runner.make_env(
        {"BPB_HOST": "192.168.1.10", "BPB_PASSWORD": "qwerty", "BPB_PORT": "20000",}
    )
    for subs in ["cover", "light", "list", "raw"]:
        help_result = runner.invoke(cli.main, [subs, "--help",], env=env)
        assert help_result.exit_code == 0

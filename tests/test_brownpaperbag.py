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

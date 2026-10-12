import v2r
import v2r.look
import v2r.render
import v2r.settings
from v2r.__main__ import main


def test_version_is_set():
    assert v2r.__version__


def test_cli_runs_without_arguments():
    assert main([]) == 0

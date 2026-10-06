#!/usr/bin/env python3
"""Build luced-browser's headless tests in a temporary package and run them: no window, the
engine running for real (luced-2d's runner, for this application)."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--luce', type=Path, default=Path(shutil.which('luce') or ROOT.parent / 'luce/build/luce'))
parser.add_argument('--diagnostic', action='store_true', help="build with luce-base's diagnostic profile")
arguments = parser.parse_args()
with tempfile.TemporaryDirectory(prefix='luced-browser-tests-') as temp:
    project = Path(temp) / 'application'
    shutil.copytree(ROOT / 'src', project / 'src')
    for module in [*(ROOT / 'tests').glob('*.luc'), *(ROOT / 'tests').glob('*.lucb')]:
        shutil.copy2(module, project / 'src' / module.name)
    # The application's own dependencies, each taken from the checkout beside this one.
    manifest = (ROOT / 'package.prisma').read_text()
    dependencies = ''.join('    def dependency "%s" {\n        str owner = "dymokomi"\n        str path = %s\n    }\n' % (name, json.dumps(str(ROOT.parent / name)))
                           for name in re.findall(r'def dependency "([^"]+)"', manifest))
    (project / 'package.prisma').write_text('#prisma 4.0\ndef package "luced-browser-tests" {\n    str owner = "dymokomi"\n    str version = "0.0.0"\n    str kind = "tool"\n    str language = "luce"\n    str entry = "src/main.luc"\n' + dependencies + '}\n')
    binary = Path(temp) / 'tests'
    profile = ['--profile', 'diagnostic'] if arguments.diagnostic else []
    subprocess.run([str(arguments.luce.resolve()), 'build', str(project / 'src/main.luc'), *profile, '-o', str(binary)], check=True, timeout=900)
    # The pages, and a directory of the run's own for the files the tests write.
    scratch = Path(temp) / 'scratch'
    scratch.mkdir()
    subprocess.run([str(binary), str(ROOT / 'tests/pages'), str(scratch)], check=True, timeout=300)

#!/usr/bin/env python3
"""The size of a luced-browser executable, by package and module.

    python3 tools/binary_size.py [build/luced-browser] [--top N]

Reads the symbol table (`nm -n`) and gives each code symbol the bytes up to the next symbol.
Luce Base names a symbol `lb_<length><module path>_...`: the length-prefixed path names the
package and module that define it (`luce_browser_engine_web`, `luce_browser_render_raster`);
generic code instantiated elsewhere counts for the module that defines the generic (most of
`ak`'s vectors and hash tables). Symbols of the compiler's runtime and the program's main
module are counted as such; anything else (system stubs) as "other". Prints the segments,
then the modules largest first with their share of the code, and the size the executable
would have stripped of its symbol table.
"""
import collections
import os
import re
import subprocess
import sys
import tempfile

PATH = re.compile(r'^_?lb_(\d+)(.*)$')


def module_of(name):
    match = PATH.match(name)
    if not match:
        if name.lstrip('_').startswith('lb_main'):
            return 'luced-browser (main)'
        if name.lstrip('_').startswith('lb_'):
            return 'luce-base runtime'
        return 'other'
    length = int(match.group(1))
    return match.group(2)[:length]


def code_sizes(binary):
    lines = subprocess.run(['nm', '-n', binary], capture_output=True, text=True, check=True).stdout.splitlines()
    symbols = []
    for line in lines:
        parts = line.split()
        if len(parts) == 3 and parts[1] in ('T', 't'):
            symbols.append((int(parts[0], 16), parts[2]))
    sizes = collections.Counter()
    for (address, name), (following, _) in zip(symbols, symbols[1:]):
        sizes[module_of(name)] += following - address
    return sizes


def stripped_size(binary):
    with tempfile.TemporaryDirectory() as directory:
        copy = os.path.join(directory, 'stripped')
        subprocess.run(['strip', '-o', copy, binary], check=True, capture_output=True)
        return os.path.getsize(copy)


def main():
    arguments = [a for a in sys.argv[1:] if not a.startswith('--')]
    top = 25
    if '--top' in sys.argv:
        top = int(sys.argv[sys.argv.index('--top') + 1])
        arguments = [a for a in arguments if a != str(top)]
    binary = arguments[0] if arguments else 'build/luced-browser'
    print(f'{binary}: {os.path.getsize(binary):,} bytes, {stripped_size(binary):,} stripped')
    print(subprocess.run(['size', '-m', binary], capture_output=True, text=True).stdout.strip())
    sizes = code_sizes(binary)
    total = sum(sizes.values())
    print(f'\ncode by module ({total:,} bytes):')
    for module, size in sizes.most_common(top):
        print(f'  {size:>12,}  {100.0 * size / total:5.1f}%  {module}')
    rest = sum(size for _, size in sizes.most_common()[top:])
    if rest:
        print(f'  {rest:>12,}  {100.0 * rest / total:5.1f}%  ({len(sizes) - top} more)')


if __name__ == '__main__':
    main()

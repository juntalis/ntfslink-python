"""Builds the optional ``ntfslink._cext`` speedup extension.

A missing/broken C toolchain must not fail the overall install — the
package works fine on the pure-Python fallback backend. This mirrors the
pattern used by MarkupSafe/PyYAML for their optional C speedups.
"""
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
from setuptools.errors import CompileError, ExecError, PlatformError


class optional_build_ext(build_ext):
    def run(self):
        try:
            super().run()
        except PlatformError as exc:
            print(f'WARNING: could not build the ntfslink C extension, skipping: {exc}')

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except (CompileError, ExecError, PlatformError) as exc:
            print(f'WARNING: could not build the ntfslink C extension, skipping: {exc}')


ext_modules = [
    Extension(
        'ntfslink._cext',
        sources=['src/ntfslink/_cext/_cext.c'],
        libraries=['advapi32'],
    ),
]

setup(
    ext_modules=ext_modules,
    cmdclass={'build_ext': optional_build_ext},
)

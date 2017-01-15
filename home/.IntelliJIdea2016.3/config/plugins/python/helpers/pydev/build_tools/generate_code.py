'''
This module should be run to recreate the files that we generate automatically
(i.e.: modules that shouldn't be traced and cython .pyx)
'''

from __future__ import print_function

import os
import struct



def is_python_64bit():
    return (struct.calcsize('P') == 8)

root_dir = os.path.join(os.path.dirname(__file__), '..')

def get_cython_contents(filename):
    if filename.endswith('.pyc'):
        filename = filename[:-1]

    state = 'regular'

    new_contents = []
    with open(filename, 'r') as stream:
        for line in stream:
            strip = line.strip()
            if state == 'regular':
                if strip == '# IFDEF CYTHON':
                    state = 'cython'

                    new_contents.append('%s -- DONT EDIT THIS FILE (it is automatically generated)\n' % line.replace('\n', '').replace('\r', ''))
                    continue

                new_contents.append(line)

            elif state == 'cython':
                if strip == '# ELSE':
                    state = 'nocython'
                    new_contents.append(line)
                    continue

                elif strip == '# ENDIF':
                    state = 'regular'
                    new_contents.append(line)
                    continue

                assert strip.startswith('# '), 'Line inside # IFDEF CYTHON must start with "# ".'
                new_contents.append(line.replace('# ', '', 1))

            elif state == 'nocython':
                if strip == '# ENDIF':
                    state = 'regular'
                    new_contents.append(line)
                    continue
                new_contents.append('# %s' % line)

    assert state == 'regular', 'Error: # IFDEF CYTHON found without # ENDIF'


    return ''.join(new_contents)

def _generate_cython_from_files(target, modules):
    contents = ['''# Important: Autogenerated file.

# DO NOT edit manually!
# DO NOT edit manually!
''']

    for mod in modules:
        contents.append(get_cython_contents(mod.__file__))

    with open(target, 'w') as stream:
        stream.write(''.join(contents))

def generate_dont_trace_files():
    template = '''# Important: Autogenerated file.

# DO NOT edit manually!
# DO NOT edit manually!

from _pydevd_bundle.pydevd_constants import IS_PY3K

LIB_FILE = 1
PYDEV_FILE = 2

DONT_TRACE = {
    # commonly used things from the stdlib that we don't want to trace
    'Queue.py':LIB_FILE,
    'queue.py':LIB_FILE,
    'socket.py':LIB_FILE,
    'weakref.py':LIB_FILE,
    '_weakrefset.py':LIB_FILE,
    'linecache.py':LIB_FILE,
    'threading.py':LIB_FILE,

    #things from pydev that we don't want to trace
    '_pydev_execfile.py':PYDEV_FILE,
%(pydev_files)s
}

if IS_PY3K:
    # if we try to trace io.py it seems it can get halted (see http://bugs.python.org/issue4716)
    DONT_TRACE['io.py'] = LIB_FILE

    # Don't trace common encodings too
    DONT_TRACE['cp1252.py'] = LIB_FILE
    DONT_TRACE['utf_8.py'] = LIB_FILE
'''

    pydev_files = []

    for root, dirs, files in os.walk(root_dir):
        for d in [
            '.git',
            '.settings',
            'build',
            'build_tools',
            'dist',
            'pydevd.egg-info',
            'pydevd_attach_to_process',
            'pydev_sitecustomize',
            'stubs',
            'tests',
            'tests_mainloop',
            'tests_python',
            'tests_runfiles',
            'test_pydevd_reload',
            'third_party',
            '__pycache__',
            '_pydev_runfiles',
            'pydev_ipython',
        ]:
            try:
                dirs.remove(d)
            except:
                pass

        for f in files:
            if f.endswith('.py'):
                if f not in (
                        '__init__.py',
                        'runfiles.py',
                        'pydev_coverage.py',
                        'pydev_pysrc.py',
                        'setup.py',
                        'setup_cython.py',
                        'interpreterInfo.py',
                ):
                    pydev_files.append("    '%s': PYDEV_FILE," % (f,))

    contents = template % (dict(pydev_files='\n'.join(sorted(pydev_files))))
    assert 'pydevd.py' in contents
    assert 'pydevd_dont_trace.py' in contents
    with open(os.path.join(root_dir, '_pydevd_bundle', 'pydevd_dont_trace_files.py'), 'w') as stream:
        stream.write(contents)

def remove_if_exists(f):
    try:
        if os.path.exists(f):
            os.remove(f)
    except:
        import traceback;traceback.print_exc()

def generate_cython_module():
    remove_if_exists(os.path.join(root_dir, '_pydevd_bundle', 'pydevd_cython.pyx'))

    target = os.path.join(root_dir, '_pydevd_bundle', 'pydevd_cython.pyx')
    curr = os.environ.get('PYDEVD_USE_CYTHON')
    try:
        os.environ['PYDEVD_USE_CYTHON'] = 'NO'

        from _pydevd_bundle import pydevd_additional_thread_info_regular
        from _pydevd_bundle import pydevd_frame, pydevd_trace_dispatch_regular
        _generate_cython_from_files(target, [pydevd_additional_thread_info_regular, pydevd_frame, pydevd_trace_dispatch_regular])
    finally:
        if curr is None:
            del os.environ['PYDEVD_USE_CYTHON']
        else:
            os.environ['PYDEVD_USE_CYTHON'] = curr

if __name__ == '__main__':
    generate_dont_trace_files()
    generate_cython_module()

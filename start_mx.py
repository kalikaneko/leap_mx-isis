#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
                ____
               | MX |_________________________
            ___|____| An encrypting remailer  |________
           |       |__________________________|        |
           | is designed for use on a mail exchange    |
           | with OpenPGP implementations and Postfix, |
           | and is part of the Leap Encryption Access |
           | Project platform.                         |
           |___________________________________________|
"""
    # authors:   Isis Agora Lovecruft, <isis@leap.se> 0x2cdb8b35
    # license:   AGPLv3, see included LICENCE file.
    # copyright: copyright (c) 2013 Isis Agora Lovecruft


from __future__ import print_function
from os         import getcwd
from os         import path as ospath

import sys


application_name = "leap_mx"

def __get_dirs__():
    """Get the absolute path of the top-level repository directory."""
    here = getcwd()
    base = here.rsplit(application_name, 1)[0]
    repo = ospath.join(base, application_name)
    leap = ospath.join(repo, 'src')
    ours = ospath.join(leap, application_name.replace('_', '/'))
    return repo, leap, ours

## py3k check, snagged from python-gnupg-0.3.2 by Vinay Sajip
try:
    unicode
    _py3k = False
except NameError:
    _py3k = True

## Set the $PYTHONPATH:
repo, leap, ours = __get_dirs__()
sys.path[:] = map(ospath.abspath, sys.path)
sys.path.insert(0, leap)

## Now we should be able to import ourselves without installation:
try:
    from leap.mx      import runner
    from leap.mx.util import config, log, version
except ImportError, ie:
    print("%s \nExiting... \n" % ie.message)
    sys.exit(1)

try:
    from twisted.python      import usage, runtime, failure
    from twisted.python.util import spewer
except ImportError, ie:
    print("This software requires Twisted>=12.0.2, please see the README for")
    print("help on using virtualenv and pip to obtain requirements.")


class MXOptions(usage.Options):
    """Command line options for leap_mx."""

    optParameters = [
        ['config', 'c', 'mx.conf', 'Config file to use']]
    optFlags = [
        ['all-tests', 'a', 'Run all unittests'],
        ['verbose', 'v', 'Increase logging verbosity']]

    def opt_version(self):
        """Print leap_mx version and exit."""
        print("Authors:   %s" % version.getAuthors())
        print("Licence:   AGPLv3, see included LICENSE file")
        print("Copyright: © 2013 Isis Lovecruft, see included COPYLEFT file")
        print("Version:   %s" % version.getVersion())
        sys.exit(0)

    def opt_spewer(self):
        """Print *all of the things*. Useful for debugging."""
        sys.settrace(spewer)

    def parseArgs(self):
        """Called with the remaining unrecognised commandline options."""
        log.warn("Couldn't recognise option: %s" % self)


if __name__ == "__main__":
    dependency_check = runner.CheckRequirements(version.getPackageName(),
                                                version.getPipfile())
    ## the following trickery is for printing the module docstring
    ## *before* the options help, and printing it only once:
    import __main__
    print("%s" % __main__.__doc__)
    __main__.__doc__ = ("""
Example Usage:
  $ start_mx.py --config="./my-mx.conf" --spewer
""")

    mx_options = MXOptions()
    if len(sys.argv) <= 1:
        mx_options.opt_help()
        sys.exit(0)
    try:
        mx_options.parseOptions()
    except usage.UsageError, ue:
        print("%s" % ue.message)
        sys.exit(1)
    options = mx_options.opts

    ## Get the config settings:
    config.filename = options['config']
    config.loadConfig()

    if config.basic.enable_logfile:
        ## Log to file:
        logfilename = config.basic.logfile
        logfilepath = ospath.join(repo, 'logs')
        log.start(logfilename, logfilepath)
    else:
        ## Otherwise just log to stdout:
        log.start()

    log.msg("Testing logging functionality")
    if runtime.platform.supportsThreads():
        thread_support = "with thread support."
    else:
        thread_support = "without thread support."
    log.debug("Running %s, with Python %s on %s platform %s"
              % (application_name, runtime.shortPythonVersion(),
                 runtime.platform.getType(), thread_support))

    if options['verbose']:
        config.basic.debug = True
        failure.traceupLength = 7
        failure.startDebugMode()

    if options['all-tests']:
        from leap.mx import tests
        tests.run()
    else:
        mx_options.getUsage()
        sys.exit(1)

#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys, os
import json
import optparse
import time
import logging
import subprocess

from twisted.internet import reactor, protocol

try:
    # fail gently if the dependency is missing, explain where to get it
    import psutil
except ImportError:
    print("psutil module is required for process tracking. Please see: https://code.google.com/p/psutil/")


__author__ = "Luis Rodil-Fernandez <root@derfunke.net>"
__version__ = "0.9b"

def is_server_running():
    """Get a list of running tmsi_server processes"""
    try:
        procs = [p for p in psutil.get_process_list() if 'tmsi_server' in p.name]
        return procs
    except psutil.NoSuchProcess as e:
        return False

# ###########################################################################
class LauncherException(Exception):
    pass

class NexusNotFoundException(Exception):
    pass

class NexusLauncher:
    def __init__(self, experiment):
        self.proc = None
        self.experiment = experiment

    def launch(self, cfg):
        """Start the TMSi server process """
        path = os.path.join("./denissen/nexus", "tmsi_server")

        print "(i) Start NEXUS {0} serving on port {1}".format(cfg['mac'], cfg['port'])

        # create channel flags string
        chflags = "".join(str(v) for v in cfg['channels'].keys()) # ''.join(str(v) for v in seq)
        #print "cflags: {0}".format(chflags)
        chnames = None
        chans = []
        #print cfg['channels']
        # create a -CHx name param
        for k, v in cfg['channels'].iteritems():
            ch = "-{0} {1} ".format(k, v)
            chans.append( ch )

        #print chans

        chparam = " ".join(chans)
        # ./tmsi_server -a 00:A0:96:1B:48:15 -c EF -E soft -F overstretched -s 4 -i exp
        cmd = "-a {0} -s 4 -i {1}-{2} -c {3} {4} -port {5}".format(cfg['mac'], self.experiment, cfg['id'], chflags, chparam, cfg['port'])
        #print cmd
        logging.debug("Execute TMSi server %s" % (cmd,))

        # @todo redirect stdout and stderr to /dev/null, perhaps we want to send this output somewhere else?
        f = open(os.devnull, 'w')
        try:
            # prepare argument list for Popen
            args = [path] + cmd.split() #[path].append( cmd.split() ) #, "--config", cfgfile, "--log", logfile]
            print args
            self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            time.sleep(0.3)
            self.proc.poll()
            if self.proc.returncode:#   != 0:
                msg = "Executing external TMSi Server process failed returning %s" % (self.proc.returncode,)
                for line in iter(self.proc.stdout.readline, b''):
                    print(">>> " + line.rstrip())
                # log error and propagate condition
                logging.error(msg)
                raise LauncherException(msg)
        except OSError, e:
            msg = "Couldn't execute subprocess '%s'" % (path,)
            # log and propagate
            logging.critical(msg)
            raise LauncherException(msg)

    def terminate(self):
        """Terminate all Nexus processes that might be running"""
        logging.debug("Terminating TMSi server subprocess")
        try:
            procs = is_server_running()
            if procs: # process found, terminate it
                for p in procs:
                    p.terminate()  # NoSuchProcess: process no longer exists (pid=2476)
        except (psutil.NoSuchProcess, psutil.AccessDenied), err:
            logging.error("exception while trying to shut down process for pid:%s, reason:%s" % (err.pid, err.msg))


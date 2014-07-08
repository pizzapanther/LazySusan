#!/usr/bin/env python

import os
import datetime
import subprocess

import pyinotify

class LessCompile (pyinotify.ProcessEvent):
  def __init__ (self, ldir, *args, **kwargs):
    self.ldir = ldir
    super(LessCompile, self).__init__(*args, **kwargs)
    
  def process_IN_CLOSE (self, event):
    if event.mask == pyinotify.IN_CLOSE_WRITE and event.pathname.endswith('.less'):
      print("Processing lazysusan.less " + unicode(datetime.datetime.now()))
      
      subprocess.call(
        "lessc {ldir}/lazysusan.less {ldir}/lazysusan.css".format(ldir=self.ldir),
        shell=True
      )
      
def run_watcher ():
  basedir = os.path.abspath(os.path.dirname(__file__))
  os.chdir(basedir)
  
  ldir = os.path.join(basedir, 'static', 'css')
  
  wm = pyinotify.WatchManager()
  handler = LessCompile(ldir)
  notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
  wm.add_watch(ldir, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
  notifier.loop()
  
if __name__ == "__main__":
  run_watcher()
  
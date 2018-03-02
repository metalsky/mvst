#!/usr/bin/python

#
#  FILE:  task
#
#  DESCRIPTION:
#    This file contains the data types surrounding TASKS
#
#
#  AUTHOR:  MontaVista Software, Inc. <source@mvista.com>
#
#  Copyright 2006 MontaVista Software Inc.
#
#  This program is free software; you can redistribute  it and/or modify it
#  under  the terms of  the GNU General  Public License as published by the
#  Free Software Foundation;  either version 2 of the  License, or (at your
#  option) any later version.
#
#  THIS  SOFTWARE  IS PROVIDED   ``AS  IS'' AND   ANY  EXPRESS OR IMPLIED
#  WARRANTIES,   INCLUDING, BUT NOT  LIMITED  TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
#  NO  EVENT  SHALL   THE AUTHOR  BE    LIABLE FOR ANY   DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED   TO, PROCUREMENT OF  SUBSTITUTE GOODS  OR SERVICES; LOSS OF
#  USE, DATA,  OR PROFITS; OR  BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN  CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  You should have received a copy of the  GNU General Public License along
#  with this program; if not, write  to the Free Software Foundation, Inc.,
#  675 Mass Ave, Cambridge, MA 02139, USA.
#




import sys
import error


#Defines
NONFATAL = "NONFATAL"
FATAL = "FATAL"
FORK = "FORK"
FORK_ARGS = 3
SYNC = "SYNC"


#Just a tuple to make the code below a little more reader friendly
supportedOps = (FORK, SYNC)

#All exceptions are derived from the exception class
class BadForkOP(Exception):
  pass

#Data used for threading processes, init function enforces our makeshift enum
class ForkObj:
  def __init__(self, op, num=None, type=None):
    global supoprtedOps
    if op not in supportedOps:
      raise BadForkOP, "Tried to use unsupported Fork operations"
    self.forkOp = op
    self.numThrds = num
    self.remoteType = type

#Task is the basic task datatype that will be used by the parser and the execution unit
class Task:
  def __init__(self, name, pyFile, taskFile, taskLineNo, forkObj=None, taskPtr=None, fatal=NONFATAL):
    self.name = name
    self.pyFile = pyFile
    self.taskFile = taskFile
    self.taskLineNo = taskLineNo
    self.forkObj = forkObj
    self.taskPtr = taskPtr
    self.fatal = fatal


def main():
  print "No manual execution of this module"
  sys.exit(1)


if __name__ == "__main__":
  main()



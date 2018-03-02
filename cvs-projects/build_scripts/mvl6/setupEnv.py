#!/usr/bin/env python
import commands

resolv = 'search borg.mvista.com sh.mvista.com mvista.com\nnameserver 10.23.5.3'
commands.getoutput('echo %s > /etc/resolv.conf' % resolv)
commands.getoutput('source setup_env.sh')

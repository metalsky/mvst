#!/usr/bin/python

import sys, os, string

if len(sys.argv) == 1:
  print 'usage: %s' % (sys.argv[0],'<product>',)
  sys.exit(1)

product = sys.argv[1]
cd = os.getcwd()

if product == 'mvl21':
  dirs = (
	'mvl2.1-arm',
	'mvl2.1-mips',
	'mvl2.1-ppc',
	'mvl2.1-sh',
	'mvl2.1-strngarm',
	'mvl2.1-x86',
	'mvl2.1-sony'
         )
elif product == 'mvlcge21':
  dirs = ('mvlcge2.1.0',)
elif product == 'mvl30':
  dirs = 	(
	'mvl3.0-arm',
	'mvl3.0-mips',
	'mvl3.0-ppc',
	'mvl3.0-sh',
	'mvl3.0-strngarm',
	'mvl3.0-x86',
	'mvl3.0-xtensa'
		)
elif product == 'mvl30-sony':
  dirs = 	(
	'mvl3.0-sony-update1',
                )
elif product == 'mvlcge30':
  dirs = 	(
	'mvlcge3.0.0',
		)
elif product == 'mvlcee30':
  dirs = 	(
	'mvlcee3.0-ti-omap161x_innovator',
	'mvlcee3.0-ti-innovator',
	'mvlcee3.0-intel-mainstone'
		)
elif product == 'mvl31':
  dirs = 	(
	'mvl3.1-arm',
	'mvl3.1-mips',
	'mvl3.1-ppc',
	'mvl3.1-sh',
	'mvl3.1-strngarm',
	'mvl3.1-x86',
	'mvl3.1-xtensa',
		)
elif product == 'mvlcge31':
  dirs = 	(
	'mvlcge3.1-x86',
	'mvlcge3.1-ppc',
	'mvlcge3.1-strngarm',
		)
elif product == 'mvlcee31':
  dirs = 	(
	'mvlcee3.1-ti-omap16xx_gsm_gprs',
	'mvlcee3.1-hitachi-ms7300cp01',
	'mvlcee3.1-ti-omap-730_gsm_gprs',
	'mvlcee3.1-intel-mainstone-pxa27x',
	'mvlcee3.1-motorola-mx21ads',
	'mvlcee3.1-hitachi-ms73180cp01',
        'mvlcee3.1-ti-omap2420_gsm_gprs'
	#'mvlcee3.1-x86':			['x86_586',]
		)
for d in dirs:
    os.chdir('/mvista/ftp/arch/%s/updates' % (d))
    print 'I am in %s/updates and am going to update the .manifest.xml file' % (d)
    os.system('/mvista/ftp/arch/mkmanifest > .manifest.xml')
    os.chdir(cd)


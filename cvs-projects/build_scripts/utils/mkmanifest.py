#!/usr/bin/python2

import sys, os
from manifestVerify import validateManifest
cd = os.getcwd()

dirs = 	(
	'mvl3.1-arm',
	'mvl3.1-mips',
	'mvl3.1-ppc',
	'mvl3.1-sh',
	'mvl3.1-strngarm',
	'mvl3.1-x86',
	'mvl3.1-xtensa',
	'mvlcge3.1-x86',
	'mvlcge3.1-ppc',
	'mvlcge3.1-strngarm',
        'mvlcge3.1-em64t',
        'mvlcge3.1-amd64',
	'mvlcee3.1-ti-omap16xx_gsm_gprs',
	'mvlcee3.1-hitachi-ms7300cp01',
	'mvlcee3.1-ti-omap-730_gsm_gprs',
	'mvlcee3.1-intel-mainstone-pxa27x',
	'mvlcee3.1-motorola-mx21ads',
	'mvlcee3.1-hitachi-ms73180cp01',
        'mvlcee3.1-ti-omap2420_gsm_gprs',
        'mvlcee3.1-ti-omap2430_sdp',
	'mvlcee3.1-samsung-24a0', #2440 is linked to this updates
        'mvl4.0.1-x86',
	'mvl4.0.1-powerpc400',
	'mvl4.0.1-powerpc700',
	'mvl4.0.1-powerpc7400',
	'mvl4.0.1-xscale',
	'mvl4.0.1-armv5',
	'mvl4.0.1-mipsfp',
	'mvl4.0.1-powerpc64',
	'mvl4.0.1-mips64fp',
	'mvl4.0.1-powerquicci',
	'mvl4.0.1-powerquiccii',
	'mvl4.0.1-powerquicciii',
        'mvl4.0.1-mipsnfp',
        'mvlcge4.0.1-em64t',
	'mvlcge4.0.1-ppc700',
	'mvlcge4.0.1-ppc7400',
	'mvlcge4.0.1-ppc900',
	'mvlcge4.0.1-ppc85xx',
	'mvlcge4.0.1-x86',
	'mobilinux4.0.2-arm_iwmmxt',
	'mobilinux4.0.2-armv5',
	'mobilinux4.0.2-armv6',
        'mobilinux4.0.2-philips_armv5',
	'mobilinux4.1.0-arm_iwmmxt',
	'mobilinux4.1.0-armv6',
	'mobilinux4.1.0-ti-omap2430_sdp',
   )


for dir in dirs:
    os.chdir('/mvista/arch/%s/updates' % (dir))
    print 'I am in %s/updates and am going to update the manifest.xml file' % (dir)
    os.system('python /mvista/arch/mkman.py > manifest.xml')
    print "Validating..."
    validateManifest()

os.chdir(cd)


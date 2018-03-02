#!/usr/bin/python2

#this file hosts some dictionarys that our scripts are gonna pull from, its centralized so that we can start using it in more than one script


allthreeone =         {
        'cpfrom':  '/mvista/dev_area/foundation/foundation_one-updates',

        'mvl3.1-arm':                           [['arm_720t_le','arm_v4t_le'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvl3.1-mips':                          [['mips_fp_be','mips_fp_le','mips_nfp_le'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvl3.1-ppc':                           [['ppc_405','ppc_74xx','ppc_7xx','ppc_82xx','ppc_8xx','ppc_440',],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvl3.1-sh':                            [['sh_sh3_be','sh_sh3_le','sh_sh4_be','sh_sh4_le'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvl3.1-strngarm':                      [['arm_sa_le','arm_xscale_be','arm_xscale_le'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvl3.1-x86':                           [['x86_486','x86_586','x86_crusoe','x86_pentium2','x86_pentium3','x86_pentium4'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

#       'mvl3.1-xtensa':                        [['xtensa_linux_le','xtensa_linux_be'],
#                                                ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

        'mvlcge3.1-x86':                        [['x86_pentium2','x86_pentium3','x86_pentium4'],
                                                 ['redhat73','redhat80','redhat90','solaris7']],

        'mvlcge3.1-ppc':                        [['ppc_440','ppc_7xx','ppc_74xx','ppc_82xx',],
                                                 ['redhat73','redhat80','redhat90','solaris7']],

        'mvlcge3.1-strngarm':                   [['arm_xscale_be',],
                                                 ['redhat73','redhat80','redhat90','solaris7']],

        'mvlcee3.1-ti-omap16xx_gsm_gprs':       [['arm_v4t_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-hitachi-ms7300cp01':         [['sh_sh3_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-ti-omap-730_gsm_gprs':       [['arm_v4t_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-intel-mainstone-pxa27x':     [['arm_iwmmxt_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-motorola-mx21ads':           [['arm_v4t_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-hitachi-ms73180cp01':        [['sh_sh3_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-ti-omap2420_gsm_gprs':       [['arm_v5t_le',],
                                                 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-samsung-24a0':               [['arm_v4t_le',],
                                                 ['redhat73','redhat90','windows2000']]
                }

mvlspecial =        {
        'cpfrom': '/mvista/dev_area/foundation/foundation_one-updates',
        'mvl3.1-ppc':                           [['ppc_440ep','ppc_85xx'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']]
               }

mvlsixtyfour =      {
        'cpfrom': '/mvista/dev_area/foundation/foundation_one64-updates',
        'mvl3.1-mips':                          [['mips64_fp_be'],
                                                 ['redhat73','redhat90','solaris7','suse90','windows2000']],
        'mvlcge3.1-em64t':                      [['x86_em64t'],
                                                 ['redhat73','redhat80','redhat90','solaris7']],
        'mvlcge3.1-amd64':                      [['x86_amd64'],
                                                 ['redhat73','redhat80','redhat90','solaris7']]
             }


allfourzero = {
         'cpfrom':  '/mvista/dev_area/foundation/foundation_two-updates',
         'mvl4.0.1-x86':                [['x86_586',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc400':         [['ppc_440','ppc_440ep'],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc700':         [['ppc_7xx',],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc7400':        [['ppc_74xx',],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-xscale':             [['arm_xscale_be',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-armv5':              [['arm_v5t_le',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-mipsfp':             [['mips2_fp_be', 'mips2_fp_le',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc64':          [['ppc_9xx',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-mips64fp':           [['mips64_fp_be',],
                                         ['redhat90','solaris8','suse90','windows2000']],

         'mvl4.0.1-powerquiccii':       [['ppc_82xx',],
                                         ['redhat90','solaris8','suse90','windows2000']],

         'mvl4.0.1-powerquicciii':      [['ppc_85xx',],
                                         ['redhat90','solaris8','suse90','windows2000']],

         'mvl4.0.1-mipsnfp':            [['mips2_nfp_le'],
                                         ['redhat90','solaris8','suse90','windows2000']],

         'mvlcge4.0.1-x86':             [['x86_pentium3','x86_pentium4'],
                                         ['redhat90','solaris8']],
        'mvlcge4.0.1-ppc700':           [['ppc_7xx',],
                                         ['redhat90','solaris8']],

         'mvlcge4.0.1-ppc7400':          [['ppc_74xx',],
                                         ['redhat90','solaris8']],

         'mvlcge4.0.1-ppc900':           [['ppc_9xx',],
                                         ['redhat90','solaris8']],

         'mvlcge4.0.1-em64t':           [['x86_em64t',],
                                         ['redhat90','solaris8']],

         'mobilinux4.0.2-arm_iwmmxt':    [['arm_iwmmxt_le',],
                                         ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-armv6':         [['arm_v6_vfp_le',],
                                         ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-armv5':         [['arm_v5t_le',],
                                         ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-philips_armv5': [['arm_v5t_le',],
                                         ['redhat90','suse90','windows2000']]
}

def main():
  print "No Manual Execution of this module"
  return

if __name__=="__main__":
  main()



def main():
	valid_products = {
	'foundation_two':
	  [ string.split("arm_iwmmxt_le arm_v4t_le arm_v5t_le arm_v6_vfp_be arm_v6_vfp_le arm_xscale_be arm_xscale_le mips2_fp_be mips2_fp_le mips2_nfp_be mips2_nfp_le mips64_fp_be mips64_fp_le mips_vr4133_le mips_vr4133_be ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx ppc_9xx sh_sh3_le sh_sh4_le x86_586 x86_amd64 x86_em64t x86_pentium3 x86_pentium4 arm_v6_vfp_le_uclibc arm_iwmmxt_le_uclibc arm_v5t_le_uclibc mips64_octeon_be ppc_83xx_nfp xtensa_linux_be xtensa_linux_le", " "),
	   string.split("redhat90 solaris8 suse90 windows2000"," "),
	   '/mvista/dev_area/foundation/foundation_two-updates' ],
	'foundation_two_cge400':
	  [ string.split("x86_pentium3 x86_pentium4", " "),
	   string.split("redhat90 solaris8"," "),
	   '/mvista/dev_area/foundation/foundation_two-updates' ],
	'cge401':
	  [ string.split("x86_pentium3 x86_pentium4 ppc_74xx ppc_7xx ppc_9xx x86_em64t ppc_85xx ppc_440 x86_amd64", " "),
	   string.split("redhat90 solaris8"," "),
	   '/mvista/dev_area/cge/mvlcge401-updates' ],
	'mbl410':
	  [ string.split("arm_iwmmxt_le arm_iwmmxt_le_uclibc arm_v6_vfp_le arm_v6_vfp_le_uclibc", " "),
	   string.split("redhat90 windows2000 suse90"," "),
	   '/mvista/dev_area/mobilinux/mobilinux410-updates' ],
	'foundation_one':
	  [ string.split("arm_720t_be arm_720t_le arm_iwmmxt_le arm_sa_le arm_v4t_be arm_v4t_le arm_v5t_le arm_xscale_be arm_xscale_le mips_fp_be mips_fp_le mips_nfp_le ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx sh_sh3_be sh_sh3_le sh_sh4_be sh_sh4_le x86_486 x86_586 x86_crusoe x86_pentium x86_pentium2 x86_pentium3 x86_pentium4", " "),
	   string.split("mandrake91 redhat73 redhat80 redhat90 solaris7 suse90 windows2000"," "),
	   '/mvista/dev_area/foundation/foundation_one-updates' ],
	'foundation_one64':
	  [ string.split("mips64_fp_be x86_amd64 x86_em64t", " "),
	   string.split("mandrake91 redhat73 redhat80 redhat90 solaris7 suse90 windows2000"," "),
	   '/mvista/dev_area/foundation/foundation_one64-updates' ],
	'foundation-cee':
	  [ string.split("arm_iwmmxt_le arm_v4t_le arm_v5t_le sh_sh3_le x86_586 ", " "),
		string.split("redhat73 redhat90 windows2000"," "),
		'/mvista/dev_area/foundation/foundation_one-updates' ],
	'foundation-cge':
	  [ string.split("", " "),
		string.split(""," "),
		'/mvista/dev_area/foundation/foundation_one-updates' ],
	'pro':
	  [ string.split("arm_720t_le arm_sa_le arm_v4t_le arm_xscale_be arm_xscale_le mips_fp_be mips_fp_le mips_nfp_le ppc_405 ppc_440 ppc_74xx ppc_7xx ppc_82xx ppc_8xx sh_sh3_be sh_sh3_le sh_sh4_be sh_sh4_le x86_486 x86_586 x86_crusoe x86_pentium2 x86_pentium3 x86_pentium4 xtensa_linux_be xtensa_linux_le", " "),
		 string.split("mandrake91 redhat73 redhat90 solaris7 suse90 windows2000"," "),
		 '/mvista/dev_area/pro/mvl310-updates' ],
	'pro401':
	  [ string.split("arm_v4t_le arm_v5t_le arm_xscale_be arm_xscale_le mips2_fp_be mips2_fp_le mips2_nfp_le mips64_fp_be mips64_octeon_be ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx ppc_9xx ppc_9xx x86_586 mips_vr4133_be mips_vr4133_le xtensa_linux_le sh_sh4_le ppc_83xx_nfp x86_pentium3", " "),
		 string.split("redhat90 solaris8 suse90 windows2000"," "),
		 '/mvista/dev_area/pro/mvl401-updates' ],
	'cee':
	  [ "arm_v4t_le",
		 string.split("redhat73 redhat90 windows2000"," "),
		 '/mvista/dev_area/cee/mvlcee310-updates' ],
	'mobilinux':
	  [ string.split("arm_iwmmxt_le arm_v6_vfp_le arm_v5t_le", " "), string.split("redhat90 suse90 windows2000"," "), '/mvista/dev_area/mobilinux/mobilinux400-updates' ],
	'foundation_em64t':
	  [ string.split("x86_em64t", " "),
	   string.split("redhat90 redhat73 redhat80 "," "),
	   '/mvista/dev_area/foundation/foundation_em64t-updates' ],
	}

	print valid_products






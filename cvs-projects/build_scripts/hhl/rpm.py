#!/usr/bin/python
import os

def qa(grepfor,rpmbin,scripttest=0):
  if scripttest != 'true' and scripttest != 'false':
    query = os.popen(rpmbin + ' -qa | grep ' + grepfor).readlines()
    return query
  elif scripttest == 'true':
    print 'rpm.qa(' + rpmbin + ',' + grepfor
    return 0
  elif scripttest == 'false':
    print 'rpm.qa(' + rpmbin + ',' + grepfor
    return 1
    

def ba(define,buildid,target,type,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.ba() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -ba --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' +
                                  type + target + '-linux ' + extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.ba(' + define + ',' + buildid + ',' + target + ',' + type + ',' + spec + ',' + extra + ',' + rpmbuild + ')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ba(' + define + ',' + buildid + ',' + target + ',' + type + ',' + spec + ',' + extra + ',' + rpmbuild + ')'
    return 1

def ba_notarg(define,buildid,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.ba_notarg() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -ba --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' +
                                  extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.ba_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ba_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 1

def bb_notarg(define,buildid,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bb_notarg() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -bb --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' +
                                  extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bb_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bb_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 1

def bs_notarg(define,buildid,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bs_notarg() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
      os.system(rpmbuild + ' -bs --clean --define "_topdir ' + define + '" ' +
                                 '--define "_mvl_build_id ' + buildid + '" ' +
                                 '--define "vendor MontaVista Software, Inc." ' +
                                 '--define "packager <source@mvista.com>" ' +
                                 extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bs_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bs_notarg('+define+','+buildid+','+spec+','+extra+','+rpmbuild+')'
    return 1

def ba_nodef(target,type,spec,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.ba_nodef() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -ba --clean ' + type + target + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.ba_nodef('+target+','+type+','+spec+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ba_nodef('+target+','+type+','+spec+','+rpmbuild+')'
    return 1

def ba_spec(spec,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.ba_spec() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -ba --clean ' + spec)
  elif scripttest == 'true':
    print 'rpm.ba_spec('+spec+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ba_spec('+spec+','+rpmbuild+')'
    return 1

def bb(define,buildid,target,type,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bb() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -bb --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' +
                                  type + target + '-linux ' + extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bb('+define+','+buildid+','+target+','+type+','+spec+','+extra+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bb('+define+','+buildid+','+target+','+type+','+spec+','+extra+','+rpmbuild+')'
    return 1

def bahk(define,buildid,spec,extra,rpmbuild,kbv,khv,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bahk() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -ba --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "_mvl_kernel_base_version ' + kbv + '" ' +
                                  '--define "_mvl_kernel_mvl_version ' + khv + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' + extra + ' ' +
                                  spec)
  elif scripttest == 'true':
    print 'rpm.bahk('+define+','+buildid+','+spec+','+extra+','+rpmbuild+','+kbv+','+khv+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bahk('+define+','+buildid+','+spec+','+extra+','+rpmbuild+','+kbv+','+khv+')'
    return 1

def bbhk(define,buildid,spec,extra,rpmbuild,kbv,khv,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bbhk() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -bb --clean --define "_topdir ' + define + '" ' +
                                  '--define "_mvl_build_id ' + buildid + '" ' +
                                  '--define "_mvl_kernel_base_version ' + kbv + '" ' +
                                  '--define "_mvl_kernel_mvl_version ' + khv + '" ' +
                                  '--define "vendor MontaVista Software, Inc." ' +
                                  '--define "packager <source@mvista.com>" ' +
                                  extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bbhk('+define+','+buildid+','+spec+','+extra+','+rpmbuild+','+kbv+','+khv+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bbhk('+define+','+buildid+','+spec+','+extra+','+rpmbuild+','+kbv+','+khv+')'
    return 1

def bb_nodef(target,type,spec,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bb_nodef() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -bb --clean ' + type + target + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bb_nodef('+target+','+type+','+spec+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bb_nodef('+target+','+type+','+spec+','+rpmbuild+')'
    return 1

def bb_spec(spec,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bb_spec() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    return os.system(rpmbuild + ' -bb --clean ' + spec)
  elif scripttest == 'true':
    print 'rpm.bb_spec('+spec+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bb_spec('+spec+','+rpmbuild+')'
    return 1

def bs(define,buildid,target,type,spec,extra,rpmbuild,scripttest=0):
  if not os.path.exists(spec) and (scripttest != 'true' and scripttest != 'false'):
    print "rpm.bs() can't find spec file...nothing built"
    return 1
  elif scripttest != 'true' and scripttest != 'false':
    os.system(rpmbuild + ' -bs --clean --define "_topdir ' + define + '" ' +
                                 '--define "_mvl_build_id ' + buildid + '" ' +
                                 '--define "vendor MontaVista Software, Inc." ' +
                                 '--define "packager <source@mvista.com>" ' +
                                 type + target + '-linux ' + extra + ' ' + spec)
  elif scripttest == 'true':
    print 'rpm.bs('+define+','+buildid+','+target+','+type+','+spec+','+extra+','+rpmbuild+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.bs('+define+','+buildid+','+target+','+type+','+spec+','+extra+','+rpmbuild+')'
    return 1

def ivh(rpm,rpmbin,scripttest=0):
  if scripttest != 'true' and scripttest != 'false': 
    os.system(rpmbin + ' ' + rpm + ' -ivh')
  elif scripttest == 'true':
    print 'rpm.ivh('+rpm+','+rpmbin+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ivh('+rpm+','+rpmbin+')'
    return 1

def uvh(rpm,rpmbin,scripttest=0):
  if scripttest != 'true' and scripttest != 'false': 
    os.system(rpmbin + ' ' + rpm + ' -Uvh')
  elif scripttest == 'true':
    print 'rpm.uvh('+rpm+','+rpmbin+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.uvh('+rpm+','+rpmbin+')'
    return 1

def ev(rpm,rpmbin,scripttest=0):
  if scripttest != 'true' and scripttest != 'false':
    os.system(rpmbin + ' -ve ' + rpm)
  elif scripttest == 'true':
    print 'rpm.ev('+rpm+','+rpmbin+')'
    return 0
  elif scripttest == 'false':
    print 'rpm.ev('+rpm+','+rpmbin+')'
    return 1

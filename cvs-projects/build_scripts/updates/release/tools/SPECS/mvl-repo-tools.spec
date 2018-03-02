%define	f_build			f5_080218_0800385

%define mvl_install		opt/montavista/common
%define dev_foundation		/mvista/dev_area/foundation/
%define repo_prefix		/opt/mvl-repo-tools

%define _host_arch		%( uname -m | sed s/i.86/i386/ )


# We don't want to build a debug package, even if the host supports it
%undefine _enable_debug_packages

summary         : MontaVista apt-rpm repo tools 
Name            : mvl-repo-tools
%define apt_version 0.5.15lorg3.2
Version         : %{apt_version}
Release         : 5.0.1

Source0		: %{name}.tar.gz

License         : GPL/LGPL
Group           : base
Buildroot       : %{_tmppath}/%{name}-root
BuildArch	: %{_host_arch}


%description
This package provides MontaVista specific versions of apt-rpm's repo 
tools, that are designed for internal Montavista use only.


%prep

%setup -q -n %{name}


#Dev path
%ifarch x86_64
DEVDIR=%{dev_foundation}%{f_build}/build/host/centos3_64
%else
DEVDIR=%{dev_foundation}%{f_build}/build/host/centos3
%endif



#Common rpm
RPM_RPMS=`ls -1 $DEVDIR | grep common-rpm`
for RPM in $RPM_RPMS; do
  rpm2cpio $DEVDIR/$RPM | cpio -id
done

#common apt-rpm
APT_RPMS=`ls -1 $DEVDIR | grep common-apt-rpm`
for RPM in $APT_RPMS; do
  rpm2cpio $DEVDIR/$RPM | cpio -id
done

#common libxml
XML_RPMS=`ls -1 $DEVDIR | grep common-libxml`
for RPM in $XML_RPMS; do
  rpm2cpio $DEVDIR/$RPM | cpio -id
done


%build

pushd forward
gcc -D 'PROG_TO_EXEC="genbasedir"' -o mvl-genbasedir forward.c find_real_path.c
gcc -D 'PROG_TO_EXEC="genpkglist"' -o mvl-genpkglist forward.c find_real_path.c
gcc -D 'PROG_TO_EXEC="gensrclist"' -o mvl-gensrclist forward.c find_real_path.c
gcc -D 'PROG_TO_EXEC="countpkglist"' -o mvl-countpkglist forward.c find_real_path.c
popd


%install
rm -rf %{buildroot}


mkdir -p %{buildroot}%{repo_prefix}/bin
mkdir -p %{buildroot}%{repo_prefix}/apt/lib

#Install user callable binaries
cp forward/mvl-genbasedir %{buildroot}%{repo_prefix}/bin/
cp forward/mvl-genpkglist %{buildroot}%{repo_prefix}/bin/
cp forward/mvl-gensrclist %{buildroot}%{repo_prefix}/bin/
cp forward/mvl-countpkglist %{buildroot}%{repo_prefix}/bin/


#Install rpm components
cp -R %{mvl_install}/lib/rpm %{buildroot}%{repo_prefix}/apt/lib/



#Install Internal Libs
cp %{mvl_install}/lib/libapt-pkg-libc* %{buildroot}%{repo_prefix}/apt/lib/
cp %{mvl_install}/lib/libxml2* %{buildroot}%{repo_prefix}/apt/lib/
cp %{mvl_install}/lib/librpm* %{buildroot}%{repo_prefix}/apt/lib/
cp %{mvl_install}/lib/libpopt* %{buildroot}%{repo_prefix}/apt/lib/




%clean
rm -rf %{buildroot}


#Install System Libs
%files
%defattr(-,root,root)
%dir %{repo_prefix}
%dir %{repo_prefix}/bin
%dir %{repo_prefix}/apt
%dir %{repo_prefix}/apt/lib

%{repo_prefix}/bin/*
%{repo_prefix}/apt/lib/*




%changelog
* Mon Feb 25 2008 Ryan Burns <source@mvista.com>
- Fix build to make more generic
* Fri Feb 9 2007 Ryan Burns <source@mvista.com>
- First Cut

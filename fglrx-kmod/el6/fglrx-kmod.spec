
# Define the kmod package name here.
%define kmod_name fglrx

# If kversion isn't defined on the rpmbuild line, define it here.
# Due to CVE-2010-3081 patch, won't build against x86_64 kernels prior to 2.6.32-71.7.1.el6
%{!?kversion: %define kversion 2.6.32-573.el6.%{_target_cpu}}

# built for RHEL6.7
# in 14.12 the following line was useful; in 15.5 in their infinite wisdom ATI
# decided to change the naming convention again so it's not used for now
# leaving it in though as it might be needed for the next update
%define realversion 15.302

Name:    %{kmod_name}-kmod
Version: 15.12
Release: 2%{?dist}
Group:   System Environment/Kernel
License: Proprietary
Summary: AMD %{kmod_name} kernel module(s)
#AMD prohibits deep linking but loves redirects
URL:     http://support.amd.com/en-us/download

BuildRequires: redhat-rpm-config
ExclusiveArch: i686 x86_64

# I think AMD makes a special effort to make sure that no one can infer the name
# of a release from the previous one
# Sources.
# http://www2.ati.com/drivers/linux/radeon-crimson-15.12-15.302-151217a-297685e.zip
Source0:  amd-driver-installer-15.302-x86.x86_64.run
Source10: kmodtool-%{kmod_name}-el6.sh
#NoSource: 0

# Magic hidden here.
%{expand:%(sh %{SOURCE10} rpmtemplate %{kmod_name} %{kversion} "")}

# Disable the building of the debug package(s).
%define debug_package %{nil}

%description
This package provides the proprietary AMD Display Driver %{kmod_name} kernel module.
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
%setup -q -c -T
echo "override %{kmod_name} * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf
%{__mkdir_p} _kmod_build_
sh %{SOURCE0} --extract atipkg

%ifarch i686
%{__cp} -a atipkg/common/* atipkg/arch/x86/* _kmod_build_/
%endif

%ifarch x86_64
%{__cp} -a atipkg/common/* atipkg/arch/x86_64/* _kmod_build_/
%endif

# Suppress warning message
echo 'This is a dummy file created to suppress this warning: could not find /lib/modules/fglrx/build_mod/2.6.x/.libfglrx_ip.a.GCC4.cmd for /lib/modules/fglrx/build_mod/2.6.x/libfglrx_ip.a.GCC4' > _kmod_build_/lib/modules/fglrx/build_mod/2.6.x/.libfglrx_ip.a.GCC4.cmd

# proper permissions
find _kmod_build_/lib/modules/fglrx/build_mod/ -type f | xargs chmod 0644

%build
KSRC=%{_usrsrc}/kernels/%{kversion}
pushd _kmod_build_/lib/modules/fglrx/build_mod/2.6.x
    CFLAGS_MODULE="-DMODULE -DATI -DFGL -DPAGE_ATTR_FIX=0 -DCOMPAT_ALLOC_USER_SPACE=arch_compat_alloc_user_space -D__SMP__ -DMODVERSIONS"
    %{__make} CC="gcc" PAGE_ATTR_FIX=0 KVER=%{kversion} KDIR="${KSRC}" \
    MODFLAGS="$CFLAGS_MODULE" \
    CFLAGS_MODULE="$CFLAGS_MODULE" \
    LIBIP_PREFIX="%{_builddir}/%{buildsubdir}/_kmod_build_/lib/modules/fglrx/build_mod"
popd

%install
%{__install} -d %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} _kmod_build_/lib/modules/fglrx/build_mod/2.6.x/fglrx.ko \
%{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} -d %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
%{__install} -p -m 0644 atipkg/LICENSE.TXT \
%{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
# Set the module(s) to be executable, so that they will be stripped when packaged.
find %{buildroot} -type f -name \*.ko -exec %{__chmod} u+x \{\} \;
# Remove the unrequired files.
%{__rm} -f %{buildroot}/lib/modules/%{kversion}/modules.*

%clean
%{__rm} -rf %{buildroot}

%changelog
* Tue Aug 16 2016 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.12-2.el6.elrepo
- Bump version to keep in sync with fglrx-x11-drv

* Sun Feb 14 2016 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.12-1.el6.elrepo
- Update to version 15.12

* Fri Dec 18 2015 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.11-1.el6.elrepo
- Update to version 15.11

* Thu Oct 29 2015 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.9-1.el6.elrepo
- Update to version 15.9
- Strongly suggested to update due to CVE-2015-7724

* Thu Jul 28 2015 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.7-1.el6.elrepo
- Update to version 15.7

* Fri Jun 26 2015 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.5-2.el6.elrepo
- rebuilt to fix incorrect kernel deps

* Thu Jun 25 2015 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> - 15.5-1.el6.elrepo
- Update to version 15.5

* Sun Oct 19 2014 Manuel Wolfshant <wolfy@fedoraproject.org> - 14.9-1.el6_6.elrepo
- Update to version 14.9.
- Rebuilt for RHEL6.6.

* Wed Dec 04 2013 Philip J Perry <phil@elrepo.org> - 13.4-1.el6_5.elrepo
- Rebuilt for RHEL6.5

* Mon Oct 10 2013 Philip J Perry <phil@elrepo.org> - 13.4-1.el6.elrepo
- Update to version 13.4.

* Thu Feb 28 2013 Philip J Perry <phil@elrepo.org> - 13.1-1.el6.elrepo
- Update to version 13.1.

* Mon Oct 15 2012 Philip J Perry <phil@elrepo.org> - 12.8-1.el6.elrepo
- Update to version 12.8.

* Mon Jun 04 2012 Philip J Perry <phil@elrepo.org> - 12.4-1.el6.elrepo
- Update to version 12.4.

* Wed Apr 25 2012 Philip J Perry <phil@elrepo.org> - 12.3-1.el6.elrepo
- Update to version 12.3.
- Rebuild against kernel-2.6.32-220.el6

* Thu Jan 26 2012 Philip J Perry <phil@elrepo.org> - 12.1-1.el6.elrepo
- Update to version 12.1.

* Wed Dec 14 2011 Philip J Perry <phil@elrepo.org> - 11.12-2.el6.elrepo
- Rebuilt to fix http://elrepo.org/bugs/view.php?id=211

* Wed Dec 14 2011 Philip J Perry <phil@elrepo.org> - 11.12-1.el6.elrepo
- Update to version 11.12.

* Fri Nov 18 2011 Philip J Perry <phil@elrepo.org> - 11.11-1.el6.elrepo
- Update to version 11.11.

* Sat Nov 05 2011 Philip J Perry <phil@elrepo.org> - 11.10-1.el6.elrepo
- Update to version 11.10.

* Fri Oct 07 2011 Philip J Perry <phil@elrepo.org> - 11.9-2.el6.elrepo
- Rebuilt for fglrx-x11-drv update.

* Sat Oct 01 2011 Philip J Perry <phil@elrepo.org> - 11.9-1.el6.elrepo
- Update to version 11.9.

* Sat Sep 10 2011 Philip J Perry <phil@elrepo.org> - 11.8-1.el6.elrepo
- Update to version 11.8.

* Thu Jul 28 2011 Philip J Perry <phil@elrepo.org> - 11.7-1.el6.elrepo
- Update to version 11.7.

* Sat Jun 25 2011 Philip J Perry <phil@elrepo.org> - 11.6-1.el6.elrepo
- Update to version 11.6.

* Sun Jun 19 2011 Philip J Perry <phil@elrepo.org> - 11.5-4.el6.elrepo
- Rebuild for version 11.5-4.

* Fri Jun 17 2011 Philip J Perry <phil@elrepo.org> - 11.5-3.el6.elrepo
- Rebuild for version 11.5-3.

* Sat Jun 11 2011 Philip J Perry <phil@elrepo.org> - 11.5-2.el6.elrepo
- Rebuild for version 11.5-2.

* Fri Jun 03 2011 Philip J Perry <phil@elrepo.org> - 11.5-1.el6.elrepo
- Update to version 11.5.

* Fri Feb 11 2011 Philip J Perry <phil@elrepo.org> - 10.12-1.2.el6.elrepo
- bump to match fglrx-x11-drv version.

* Fri Jan 28 2011 Philip J Perry <phil@elrepo.org> - 10.12-1.el6.elrepo
- Update to version 10.12.
- Suppress warning message during compile.
- Set MODFLAGS as ATI does in build_mod/make.sh

* Fri Dec 10 2010 Philip J Perry <phil@elrepo.org> - 10.11-0.3
- Make patch fglrx-kcl_ioctl-compat_alloc.patch x86_64 specific.

* Wed Dec 08 2010 Philip J Perry <phil@elrepo.org> - 10.11-0.2
- Strip the module - ATI does in build_mod/make.sh
- Install the License

* Mon Dec 06 2010 Philip J Perry <phil@elrepo.org> - 10.11-0.1
- Patch fglrx-kcl_ioctl-compat_alloc.patch [CVE-2010-3081]
- Initial el6 build of the kmod package.

# Define the kmod package name here.
%define kmod_name ath10k

# If kversion isn't defined on the rpmbuild line, define it here.
%{!?kversion: %define kversion 3.10.0-327.el7.%{_target_cpu}}

Name:    %{kmod_name}-kmod
Version: 0.0
Release: 4%{?dist}
Group:   System Environment/Kernel
License: GPLv2
Summary: %{kmod_name} kernel module(s)
URL:     http://www.kernel.org/

BuildRequires: perl
BuildRequires: redhat-rpm-config
ExclusiveArch: x86_64

# Sources.
Source0:  %{kmod_name}-%{version}.tar.bz2
Source5:  GPL-v2.0.txt
Source10: kmodtool-%{kmod_name}-el7.sh

# Magic hidden here.
%{expand:%(sh %{SOURCE10} rpmtemplate %{kmod_name} %{kversion} "")}

# Disable the building of the debug package(s).
%define debug_package %{nil}

%description
This package provides the %{kmod_name} kernel module(s).
It is built to depend upon the specific ABI provided by a range of releases
of the same variant of the Linux kernel and not on any one specific build.

%prep
%setup -q -n %{kmod_name}-%{version}
echo "override ath * weak-updates/%{kmod_name}" > kmod-%{kmod_name}.conf
echo "override ath10k_core * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf
echo "override ath10k_pci * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf
%build
KSRC=%{_usrsrc}/kernels/%{kversion}
%{__make} -C "${KSRC}" %{?_smp_mflags} modules M=$PWD

%install
%{__install} -d %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} ath.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} %{kmod_name}/ath10k_core.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} %{kmod_name}/ath10k_pci.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} -d %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/
%{__install} %{SOURCE5} %{buildroot}%{_defaultdocdir}/kmod-%{kmod_name}-%{version}/

# strip the modules(s)
find %{buildroot} -type f -name \*.ko -exec %{__strip} --strip-debug \{\} \;

# Sign the modules(s)
%if %{?_with_modsign:1}%{!?_with_modsign:0}
# If the module signing keys are not defined, define them here.
%{!?privkey: %define privkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.priv}
%{!?pubkey: %define pubkey %{_sysconfdir}/pki/SECURE-BOOT-KEY.der}
for module in $(find %{buildroot} -type f -name \*.ko);
do %{__perl} /usr/src/kernels/%{kversion}/scripts/sign-file \
sha256 %{privkey} %{pubkey} $module;
done
%endif

%clean
%{__rm} -rf %{buildroot}

%changelog
* Sat Jun 11 2016 Philip J Perry <phil@elrepo.org> - 0.0-4
- Update to kernel-4.1.26
- fix debugfs pktlog_filter write
- fix firmware assert in monitor mode

* Wed Dec 09 2015 Philip J Perry <phil@elrepo.org> - 0.0-3
- Fix invalid NSS for 4x4 devices, backported from kernel-4.1.14

* Wed Nov 25 2015 Philip J Perry <phil@elrepo.org> - 0.0-2
- Backported from kernel-4.1.13 for RHEL-7.2

* Sat Oct 24 2015 Philip J Perry <phil@elrepo.org> - 0.0-1
- Initial el7 build of the kmod package.
- Backported from kernel-3.16.7
  [http://elrepo.org/bugs/view.php?id=601]

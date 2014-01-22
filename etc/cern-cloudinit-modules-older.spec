Name: cern-cloudinit-older
Version: 2
Release: 2.2
Summary: CERN services (cvmfs, ganglia and condor) modules for CloudInit	
Requires: cloud-init 
Conflicts: cloud-init >= 0.7.1
Group: Plugins/Contextualization
License: GPL	
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Source: https://github.com/cjdcordeiro/cloud-init-cern/raw/master/cloudinit/config/cloudinit-modules.tar.gz
Packager: CERN IT-SDC-OL
%description
This RPM copies the cloud config modules of cvmfs, Ganglia and Condor to its respective directory and prepares CloudInit to process those new modules. 

%package cvmfs
Summary: CVMFS module for CloudInit
Conflicts: cloud-init >= 0.7.1
%description cvmfs
This will only install the CVMFS module instead of installing all existing ones.

%package condor
Summary: Condor module for CloudInit
Conflicts: cloud-init >= 0.7.1
%description condor
This will only install the Condor module instead of installing all existing ones.

%package ganglia
Summary: Ganglia module for CloudInit
Conflicts: cloud-init >= 0.7.1
%description ganglia
This will only install the Ganglia module instead of installing all existing ones.

%prep
%setup -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{python_sitelib}/cloudinit/CloudConfig/
mv cc*.py %{buildroot}%{python_sitelib}/cloudinit/CloudConfig/


%pre
echo "Adding new modules to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - condor\n - cvmfs\n - ganglia"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%pre cvmfs
echo "Adding CVMFS module to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - cvmfs"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%pre condor
echo "Adding Condor module to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - condor"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%pre ganglia
echo "Adding Ganglia module to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - ganglia"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/CloudConfig/cc_condor.py
%{python_sitelib}/cloudinit/CloudConfig/cc_cvmfs.py
%{python_sitelib}/cloudinit/CloudConfig/cc_ganglia.py


%files cvmfs
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/CloudConfig/cc_cvmfs.py


%files condor
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/CloudConfig/cc_condor.py


%files ganglia
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/CloudConfig/cc_ganglia.py

%changelog
* Mon Sep 9 2013 Cristóvão Cordeiro <cristovao.cordeiro@cern.ch> 
- Production release (1.0) of the CERN-CloudInit modules, already packaged and subpackaged into this RPM.
- This RPM is meant to be installed with older versions of CloudInit (< 0.7.1)

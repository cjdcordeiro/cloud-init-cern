Name: cern-cloudinit-latest
Version: 4
Release: 4.5
Summary: CERN services (cvmfs, ganglia, shoal and condor) modules for CloudInit	
Requires: cloud-init 
Conflicts: cloud-init < 0.7.1
Group: Plugins/Contextualization
License: GPL	
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Source: https://github.com/cjdcordeiro/cloud-init-cern/raw/master/cloudinit/config/cloudinit-modules.tar.gz
Packager: CERN IT-SDC-OL
%description
This RPM copies the cloud config modules of shoal, cvmfs, Ganglia and Condor to its respective directory and prepares CloudInit to process those new modules. 

%package cvmfs
Summary: CVMFS module for CloudInit
Conflicts: cloud-init < 0.7.1
%description cvmfs
This will only install the CVMFS module instead of installing all existing ones.

%package condor
Summary: Condor module for CloudInit
Conflicts: cloud-init < 0.7.1
%description condor
This will only install the Condor module instead of installing all existing ones.

%package ganglia
Summary: Ganglia module for CloudInit
Conflicts: cloud-init < 0.7.1
%description ganglia
This will only install the Ganglia module instead of installing all existing ones.

%package shoal
Summary: Shoal module for CloudInit
Conflicts: cloud-init < 0.7.1
%description shoal
This will only install the Shoal module instead of installing all existing ones.

%prep
%setup -c

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{python_sitelib}/cloudinit/config/
mv cc*.py %{buildroot}%{python_sitelib}/cloudinit/config/

%pre
echo "Adding new modules to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - condor\n - cvmfs\n - ganglia\n - shoal"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%pre cvmfs
echo "Adding CVMFS module to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - cvmfs"
sed -i.bak "s/${old}/${newline}/g" /etc/cloud/cloud.cfg

%pre shoal
echo "Adding Shoal module to CloudInit..."
old="cloud_config_modules:"
newline="cloud_config_modules:\n - shoal"
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
%{python_sitelib}/cloudinit/config/cc_condor.py*
%{python_sitelib}/cloudinit/config/cc_cvmfs.py*
%{python_sitelib}/cloudinit/config/cc_ganglia.py*
%{python_sitelib}/cloudinit/config/cc_shoal.py*


%files cvmfs
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/config/cc_cvmfs.py*


%files condor
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/config/cc_condor.py*


%files ganglia
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/config/cc_ganglia.py*

%files shoal
%defattr(-,root,root,-)
%config(noreplace)
%{python_sitelib}/cloudinit/config/cc_shoal.py*


%changelog
* Mon Sep 9 2013 Cristóvão Cordeiro <cristovao.cordeiro@cern.ch> 
- Production release (1.0) of the CERN-CloudInit modules, already packaged and subpackaged into this RPM.
- This RPM is meant to be installed with the latest version of CloudInit (>= 0.7.1)

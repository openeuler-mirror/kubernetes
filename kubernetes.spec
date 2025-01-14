%global debug_package %{nil}
%global _buildshell  /bin/bash

Name:         kubernetes
Version:      1.25.3
Release:      1
Summary:      Container cluster management
License:      ASL 2.0
URL:          https://k8s.io/kubernetes
Source0:      https://github.com/kubernetes/kubernetes/archive/v1.25.3.tar.gz
Source1:      kube-proxy.service
Source2:      kube-apiserver.service
Source3:      kube-scheduler.service
Source4:      kube-controller-manager.service
Source5:      kubelet.service
Source6:      env-apiserver
Source7:      env-config
Source8:      env-controller-manager
Source9:      env-kubelet
Source10:     env-kubelet.kubeconfig
Source11:     env-proxy
Source12:     env-scheduler
Source13:     kubernetes-accounting.conf
Source14:     kubeadm.conf
Source15:     kubernetes.conf

Patch0001: 0001-fix-compile-options.patch
Patch0002: 0002-kubelet-support-exec-and-attach-websocket-protocol.patch
Patch0003: 0003-Escape-terminal-special-characters-in-kubectl-112553.patch
Patch0004: 0004-Return-error-for-localhost-seccomp-type-with-no-loca.patch
Patch0005: 0005-Validate-etcd-paths.patch
Patch0006: 0006-fix-node-address-validation.patch
Patch0007: 0007-Add-ephemeralcontainer-to-imagepolicy-securityaccoun.patch

%description
Container cluster management.

%package master
Summary: Kubernetes services for master host

BuildRequires: golang systemd rsync

Requires(pre): shadow-utils
Requires: kubernetes-client = %{version}-%{release}

Conflicts: kubernetes-node < %{version}-%{release}
Conflicts: kubernetes-node > %{version}-%{release}

%description master
Kubernetes services for master host.

%package node
Summary: Kubernetes services for node host

BuildRequires: golang systemd rsync

Requires(pre): shadow-utils
Requires:      docker conntrack-tools socat
Requires:      kubernetes-client = %{version}-%{release}

Conflicts: kubernetes-master < %{version}-%{release}
Conflicts: kubernetes-master > %{version}-%{release}

%description node
Kubernetes services for node host.

%package  kubeadm
Summary:  Kubernetes tool for standing up clusters

%description kubeadm
Kubernetes tool for standing up clusters.

%package client
Summary: Kubernetes client tools

BuildRequires: golang

%description client
Kubernetes client tools.

%package kubelet
Summary: Kubernetes node agent

%description kubelet
Kubernetes node agent.

%package help
Summary: Help documents for kubernetes

%description help
Help documents for kubernetes.

%prep
%autosetup -n kubernetes-%{version} -p1
mkdir -p src/k8s.io/kubernetes
mv $(ls | grep -v "^src$") src/k8s.io/kubernetes/.

%build
pushd src/k8s.io/kubernetes/
export KUBE_GIT_TREE_STATE="clean"
export KUBE_GIT_COMMIT=%{commit}
export KUBE_GIT_VERSION=v{version}
export KUBE_EXTRA_GOPATH=$(pwd)/Godeps/_workspace
export CGO_CFLAGS="-fstack-protector-strong -fPIE -D_FORTIFY_SOURCE=2 -O2"
export CGO_LDFLAGS="-Wl,-z,relro,-z,now -Wl,-z,noexecstack -pie"

make WHAT="cmd/kube-proxy"
make WHAT="cmd/kube-apiserver"
make WHAT="cmd/kube-controller-manager"
make WHAT="cmd/kubelet"
make WHAT="cmd/kubeadm"
make WHAT="cmd/kube-scheduler"
make WHAT="cmd/kubectl"

bash ./hack/generate-docs.sh
popd

%install
pushd src/k8s.io/kubernetes/
. hack/lib/init.sh
kube::golang::setup_env
output_path="${KUBE_OUTPUT_BINPATH}/$(kube::golang::host_platform)"

# install binary
install -m 755 -d %{buildroot}%{_bindir}
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kube-proxy
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kube-apiserver
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kube-controller-manager
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubelet
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubeadm
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kube-scheduler
install -p -m 755 -t %{buildroot}%{_bindir} ${output_path}/kubectl

# install service
install -d -m 0755 %{buildroot}%{_unitdir}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE1}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE2}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE3}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE4}
install -m 0644 -t %{buildroot}%{_unitdir} %{SOURCE5}

# install env
%define remove_prefix() %(echo -n %1|sed 's/.*env-//g')
install -d -m 0755 %{buildroot}%{_sysconfdir}/kubernetes
install -d -m 0700 %{buildroot}%{_sysconfdir}/kubernetes/manifests
install -m 644 -T %{SOURCE6} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE6}}
install -m 644 -T %{SOURCE7} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE7}}
install -m 644 -T %{SOURCE8} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE8}}
install -m 644 -T %{SOURCE9} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE9}}
install -m 644 -T %{SOURCE10} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE10}}
install -m 644 -T %{SOURCE11} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE11}}
install -m 644 -T %{SOURCE12} %{buildroot}%{_sysconfdir}/kubernetes/%{remove_prefix %{SOURCE12}}

# install conf
install -d -m 0755 %{buildroot}/%{_sysconfdir}/systemd/system.conf.d
install -p -m 0644 -t %{buildroot}/%{_sysconfdir}/systemd/system.conf.d %{SOURCE13}
install -d -m 0755 %{buildroot}/%{_sysconfdir}/systemd/system/kubelet.service.d
install -p -m 0644 -t %{buildroot}/%{_sysconfdir}/systemd/system/kubelet.service.d %{SOURCE14}
install -d -m 0755 %{buildroot}%{_tmpfilesdir}
install -p -m 0644 -t %{buildroot}/%{_tmpfilesdir} %{SOURCE15}

# install man
install -d %{buildroot}%{_mandir}/man1
install -p -m 644 docs/man/man1/* %{buildroot}%{_mandir}/man1

install -d -m 0755 %{buildroot}%{_datadir}/bash-completion/completions/
%{buildroot}%{_bindir}/kubectl completion bash > %{buildroot}%{_datadir}/bash-completion/completions/kubectl

install -d %{buildroot}%{_sharedstatedir}/kubelet
mkdir -p %{buildroot}/run
install -d -m 0755 %{buildroot}/run/kubernetes/
popd

mv src/k8s.io/kubernetes/*.md .
mv src/k8s.io/kubernetes/LICENSE .

%files

%files help
%{_mandir}/man1/*

%files master
%license LICENSE
%doc *.md
%attr(754, -, kube) %caps(cap_net_bind_service=ep) %{_bindir}/kube-apiserver
%{_bindir}/kube-controller-manager
%{_bindir}/kube-scheduler
%{_unitdir}/kube-apiserver.service
%{_unitdir}/kube-controller-manager.service
%{_unitdir}/kube-scheduler.service
%dir %{_sysconfdir}/kubernetes
%config(noreplace) %{_sysconfdir}/kubernetes/apiserver
%config(noreplace) %{_sysconfdir}/kubernetes/scheduler
%config(noreplace) %{_sysconfdir}/kubernetes/config
%config(noreplace) %{_sysconfdir}/kubernetes/controller-manager
%{_tmpfilesdir}/kubernetes.conf
%verify(not size mtime md5) %attr(755, kube,kube) %dir /run/kubernetes

%files node
%license LICENSE
%doc *.md
%{_bindir}/kubelet
%{_bindir}/kube-proxy
%{_unitdir}/kube-proxy.service
%{_unitdir}/kubelet.service
%dir %{_sharedstatedir}/kubelet
%dir %{_sysconfdir}/kubernetes
%dir %{_sysconfdir}/kubernetes/manifests
%config(noreplace) %{_sysconfdir}/kubernetes/config
%config(noreplace) %{_sysconfdir}/kubernetes/kubelet
%config(noreplace) %{_sysconfdir}/kubernetes/proxy
%config(noreplace) %{_sysconfdir}/kubernetes/kubelet.kubeconfig
%config(noreplace) %{_sysconfdir}/systemd/system.conf.d/kubernetes-accounting.conf
%{_tmpfilesdir}/kubernetes.conf
%verify(not size mtime md5) %attr(755, kube,kube) %dir /run/kubernetes

%files kubeadm
%license LICENSE
%doc *.md
%{_bindir}/kubeadm
%dir %{_sysconfdir}/systemd/system/kubelet.service.d
%config(noreplace) %{_sysconfdir}/systemd/system/kubelet.service.d/kubeadm.conf

%files client
%license LICENSE
%doc *.md
%{_bindir}/kubectl
%{_datadir}/bash-completion/completions/kubectl

%files kubelet
%license LICENSE
%doc *.md
%{_bindir}/kubelet
%{_unitdir}/kubelet.service

%pre master
getent group kube >/dev/null || groupadd -r kube
getent passwd kube >/dev/null || useradd -r -g kube -d / -s /sbin/nologin \
        -c "Kubernetes user" kube

%post master
%systemd_post kube-apiserver kube-scheduler kube-controller-manager

%preun master
%systemd_preun kube-apiserver kube-scheduler kube-controller-manager

%postun master
%systemd_postun kube-apiserver kube-scheduler kube-controller-manager

%pre node
getent group kube >/dev/null || groupadd -r kube
getent passwd kube >/dev/null || useradd -r -g kube -d / -s /sbin/nologin \
        -c "Kubernetes user" kube

%post node
%systemd_post kubelet kube-proxy

%preun node
%systemd_preun kubelet kube-proxy

%postun node
%systemd_postun kubelet kube-proxy

%changelog
* Fri Jul 21 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.25.3-1
- Type:update
- CVE:NA
- SUG:NA
- DESC:update to 1.25.3

* Tue Jul 04 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.24.0-5
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:fix CVE-2023-2727 and CVE-2023-2728

* Tue Jul 04 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.24.0-4
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:fix CVE-2022-3294

* Thu Jun 29 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.24.0-3
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:fix CVE-2022-3162

* Thu Jun 29 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.24.0-2
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:fix CVE-2023-2431

* Tue Jan 03 2023 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.24.0-1
- Type:update
- CVE:NA
- SUG:NA
- DESC:update to 1.24.0

* Thu Dec 08 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-16
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:add patch and fix CVE-2021-25740

* Mon Nov 28 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-15
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:fix CVE-2021-25743

* Thu Nov 17 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-14
- Type:bugfix
- CVE:NA
- SUG:NA
- DESC:update tar package from source

* Wed Nov 02 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-13
- DESC: decrease wait time

* Tue Nov 01 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-12
- DESC: add log and modify timeout

* Tue Nov 01 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-11
- DESC: timeout wait backend to frontend complete

* Mon Oct 31 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-10
- DESC: kubelet fix websocket reference nul pointer

* Tue Sep 27 2022 zhongtao <zhongtao17@huawei.com> - 1.20.2-9
- DESC: fix CVE-2022-3172

* Sat Mar 19 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-8
- DESC: kubelet attach support ws

* Wed Mar 02 2022 zhangxiaoyu <zhangxiaoyu58@huawei.com> - 1.20.2-7
- DESC: fix CVE-2021-25741

* Fri Sep 24 2021 leizhongkai<leizhongkai@huawei.com> - 1.20.2-6
- DESC: fix CVE-2021-25735 and CVE-2021-25737

* Fri Jul 30 2021 chenyanpanHW <chenyanpan@huawei.com> - 1.20.2-5
- DESC: delete -Sgit from %%autosetup

* Mon Mar 22 2021 wangfengtu <wangfengtu@huawei.com> - 1.20.2-4
- Fix compile options

* Tue Feb 09 2021 lixiang <lixiang172@huawei.com> - 1.20.2-3
- Remove go-md2man build require since it's no longer provided

* Tue Feb 2 2021 gaohuatao <gaohuatao@huawei.com> - 1.20.2-2
- Add kubelet support ws

* Wed Jan 20 2021 lixiang <lixiang172@huawei.com> - 1.20.2-1
- Bump version to v1.20.2

* Fri Sep 18 2020 xiadanni <xiadanni1@huawei.com> - 1.18.6-3
- Add kubelet package

* Sat Jul 25 2020 xiadanni <xiadanni1@huawei.com> - 1.18.6-1
- Package init

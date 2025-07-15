Summary:	sslh - ssl/ssh multiplexer
Summary(pl.UTF-8):	multiplekser ssl/ssh
Name:		sslh
Version:	1.20
Release:	0.1
License:	GPL v2+
Group:		Applications
Source0:	http://www.rutschle.net/tech/sslh/%{name}-v%{version}.tar.gz
# Source0-md5:	6a69c6128d0349e5fb22167675d18aee
Source1:	%{name}.sysconfig
Source2:	%{name}.init
Source3:	%{name}.service
Patch3:		%{name}-man.patch
URL:		http://www.rutschle.net/tech/sslh/README.html
BuildRequires:	libwrap-devel
BuildRequires:	perl-tools-pod
BuildRequires:	rpmbuild(macros) >= 1.644
Requires(postun):	/usr/sbin/userdel
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/useradd
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 38
Provides:	group(sslh)
Provides:	user(sslh)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
sslh accepts HTTPS, SSH, OpenVPN, tinc and XMPP connections on the
same port. This makes it possible to connect to any of these servers
on port 443 (e.g. from inside a corporate firewall, which almost never
block port 443) while still serving HTTPS on that port.

%description -l pl.UTF-8
sslh akceptuje połączenia HTTPS, SSH, OpenVPN, tinc oraz XMPPP na tym
samym porcie. Pozwala to na nawiązanie połączenie z którąkolwiek z
tych usług na porcie 443 (n.p. zza firmowego firewalla, który rzadko
kiedy blokuje połączenia na ten port) równolegle z usługami HTTPS.

%prep
%setup -q -n %{name}-v%{version}
%patch -P3 -p1

%build
%{__make} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags}" \
	LDFLAGS="%{rpmldflags}" \
	USELIBWRAP=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{systemdunitdir}}

%{__make} install \
	PREFIX="%{_prefix}" \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/sslh
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/sslh
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 277 sslh
%useradd -u 277 -r -d /usr/share/empty -s /bin/false -c "sslh user" -g sslh sslh

%post
/sbin/chkconfig --add sslh
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service sslh stop
	/sbin/chkconfig --del sslh
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove sslh
	%groupremove sslh
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc ChangeLog README*
%attr(754,root,root) /etc/rc.d/init.d/sslh
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/sslh
%attr(755,root,root) %{_sbindir}/*
%{_mandir}/man8/sslh.8*
%{systemdunitdir}/%{name}.service

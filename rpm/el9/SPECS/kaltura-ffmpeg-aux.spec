# EL9 bridge package: /opt/kaltura/bin/ffmpeg-aux points at the same RPM Fusion ffmpeg.
%define kaltura_bin /opt/kaltura/bin

Summary: Kaltura - auxiliary FFmpeg (RPM Fusion ffmpeg)
Name: kaltura-ffmpeg-aux
Version: 5.1
Release: 1%{?dist}
License: AGPLv3+
Group: Applications/Multimedia
URL: https://github.com/jniltinho/platform-install-packages
BuildArch: noarch
Requires: ffmpeg >= %{version}

%description
Bridge package for Rocky Linux 9: exposes the RPM Fusion ffmpeg binary
as /opt/kaltura/bin/ffmpeg-aux, the path Kaltura CE expects.

%install
mkdir -p %{buildroot}%{kaltura_bin}
ln -s %{_bindir}/ffmpeg %{buildroot}%{kaltura_bin}/ffmpeg-aux

%files
%{kaltura_bin}/ffmpeg-aux

%changelog
* Thu Sep 24 2026 Nilton OS <jniltinho@gmail.com> - 5.1-1
- Rocky Linux 9 bridge over the RPM Fusion ffmpeg.

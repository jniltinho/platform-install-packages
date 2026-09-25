# EL9 bridge package: Kaltura CE expects ffmpeg, ffprobe and qt-faststart under /opt/kaltura/bin.
# Rocky Linux 9 gets them from the RPM Fusion ffmpeg package instead of building ffmpeg 4.4 from source.
%define kaltura_bin /opt/kaltura/bin

Summary: Kaltura - FFmpeg (RPM Fusion ffmpeg)
Name: kaltura-ffmpeg
Version: 5.1
Release: 1%{?dist}
License: AGPLv3+
Group: Applications/Multimedia
URL: https://github.com/jniltinho/platform-install-packages
BuildArch: noarch
Requires: ffmpeg >= %{version}

%description
Bridge package for Rocky Linux 9: exposes the RPM Fusion ffmpeg binaries
at the /opt/kaltura paths Kaltura CE expects.

%install
mkdir -p %{buildroot}%{kaltura_bin}
for BIN in ffmpeg ffprobe qt-faststart; do
	ln -s %{_bindir}/$BIN %{buildroot}%{kaltura_bin}/$BIN
done

%files
%{kaltura_bin}/ffmpeg
%{kaltura_bin}/ffprobe
%{kaltura_bin}/qt-faststart

%changelog
* Thu Sep 24 2026 Nilton OS <jniltinho@gmail.com> - 5.1-1
- Rocky Linux 9 bridge over the RPM Fusion ffmpeg.

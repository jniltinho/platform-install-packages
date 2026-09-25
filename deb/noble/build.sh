#!/bin/bash
# Builds the Kaltura All-In-One .deb packages for Ubuntu 24.04 into /vagrant/deb/noble/repo.
# Usage: build.sh [package ...]   (no arguments = full set)
set -euo pipefail

PACKAGES="kaltura-postinst kaltura-ffmpeg kaltura-ffmpeg-aux kaltura-sphinx kaltura-base
kaltura-kmcng kaltura-html5lib kaltura-html5lib3 kaltura-html5-studio kaltura-html5-studio3
kaltura-html5-analytics kaltura-front kaltura-batch kaltura-db kaltura-nginx
kaltura-elasticsearch kaltura-server"
[ $# -gt 0 ] && PACKAGES="$*"

# SRC/REPO default to the Vagrant layout; CI sets SRC to the checkout
SRC=${SRC:-/vagrant}
REPO=${REPO:-$SRC/deb/noble/repo}
WORK=~/sources/platform-install-packages
SUDO=; [ "$(id -u)" -ne 0 ] && SUDO=sudo

$SUDO env DEBIAN_FRONTEND=noninteractive apt-get update -qq
$SUDO env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y -qq \
	build-essential devscripts debhelper dpkg-dev fakeroot rsync wget curl unzip zip bzip2 dos2unix \
	libssl-dev libpcre3-dev zlib1g-dev libxml2-dev libxslt1-dev libgd-dev libgeoip-dev \
	libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libavfilter-dev libswresample-dev >/dev/null

# the recipes expect the repo in ~/sources/platform-install-packages and sources in ~/rpmbuild/SOURCES
mkdir -p ~/sources ~/rpmbuild
[ -e ~/rpmbuild/SOURCES ] || ln -s ~/sources ~/rpmbuild/SOURCES
rsync -a --delete --exclude .git --exclude .vagrant --exclude "deb/*/repo" --exclude "rpm/*/repo" --exclude kaltura-console "$SRC/" "$WORK/"
[ -r $WORK/build/packager.rc ] || sed -e 's/@PACKAGER_NAME@/Kaltura CE/' -e 's/@PACKAGER_MAIL@/noreply@kaltura.org/' $WORK/build/packager.template.rc > $WORK/build/packager.rc

mkdir -p "$REPO"
for pkg in $PACKAGES; do
	echo "===== $pkg"
	cd $WORK/deb/$pkg
	if ! dpkg-buildpackage -b -uc -us -d > ../$pkg.build.log 2>&1; then
		tail -40 ../$pkg.build.log
		echo "FAILED: $pkg (full log: $WORK/deb/$pkg.build.log)"
		exit 1
	fi
	cp ../${pkg}_*.deb "$REPO/"
done

cd "$REPO"
dpkg-scanpackages --multiversion . /dev/null 2>/dev/null | gzip -9c > Packages.gz
echo "Repository: $REPO"
ls -1 *.deb

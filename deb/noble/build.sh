#!/bin/bash
# Gera os .deb do Kaltura All-In-One para Ubuntu 24.04 e publica em /vagrant/deb/noble/repo.
# Uso: build.sh [pacote ...]   (sem argumentos = conjunto completo)
set -euo pipefail

PACKAGES="kaltura-postinst kaltura-ffmpeg kaltura-ffmpeg-aux kaltura-sphinx kaltura-base
kaltura-kmcng kaltura-html5lib kaltura-html5lib3 kaltura-html5-studio kaltura-html5-studio3
kaltura-html5-analytics kaltura-front kaltura-batch kaltura-db kaltura-nginx
kaltura-elasticsearch kaltura-server"
[ $# -gt 0 ] && PACKAGES="$*"

SRC=/vagrant
REPO=$SRC/deb/noble/repo
WORK=~/sources/platform-install-packages

sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=a apt-get install -y -qq \
	build-essential devscripts debhelper dpkg-dev fakeroot rsync wget curl unzip zip bzip2 dos2unix \
	libssl-dev libpcre3-dev zlib1g-dev libxml2-dev libxslt1-dev libgd-dev libgeoip-dev \
	libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libavfilter-dev libswresample-dev >/dev/null

# as receitas esperam o repo em ~/sources/platform-install-packages e as fontes em ~/rpmbuild/SOURCES
mkdir -p ~/sources ~/rpmbuild
[ -e ~/rpmbuild/SOURCES ] || ln -s ~/sources ~/rpmbuild/SOURCES
rsync -a --delete --exclude .git --exclude deb/noble/repo --exclude .vagrant "$SRC/" "$WORK/"
[ -r $WORK/build/packager.rc ] || sed -e 's/@PACKAGER_NAME@/Kaltura CE/' -e 's/@PACKAGER_MAIL@/noreply@kaltura.org/' $WORK/build/packager.template.rc > $WORK/build/packager.rc

mkdir -p "$REPO"
for pkg in $PACKAGES; do
	echo "===== $pkg"
	cd $WORK/deb/$pkg
	if ! dpkg-buildpackage -b -uc -us -d > ../$pkg.build.log 2>&1; then
		tail -40 ../$pkg.build.log
		echo "FALHOU: $pkg (log completo em $WORK/deb/$pkg.build.log)"
		exit 1
	fi
	cp ../${pkg}_*.deb "$REPO/"
done

cd "$REPO"
dpkg-scanpackages --multiversion . /dev/null 2>/dev/null | gzip -9c > Packages.gz
echo "Repositório: $REPO"
ls -1 *.deb

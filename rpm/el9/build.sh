#!/bin/bash
# Builds the Kaltura All-In-One RPMs for Rocky Linux 9 into /vagrant/rpm/el9/repo.
# Usage: build.sh [package ...]   (no arguments = full set)
set -euo pipefail

PACKAGES="kaltura-postinst kaltura-monit kaltura-ffmpeg kaltura-ffmpeg-aux kaltura-sphinx kaltura-base
kaltura-kmcng kaltura-html5lib kaltura-html5lib3 kaltura-html5-studio kaltura-html5-studio3
kaltura-html5-analytics kaltura-front kaltura-batch kaltura-nginx kaltura-elasticsearch kaltura-server"
[ $# -gt 0 ] && PACKAGES="$*"

# SRC/REPO default to the Vagrant layout; CI sets SRC to the checkout
SRC=${SRC:-/vagrant}
REPO=${REPO:-$SRC/rpm/el9/repo}
SUDO=; [ "$(id -u)" -ne 0 ] && SUDO=sudo
WORK=~/sources/platform-install-packages
LOGS=~/build-logs

# --- build dependencies (EPEL + CRB for librdkafka-devel, RPM Fusion for ffmpeg-devel) ---
if [ ! -f /etc/yum.repos.d/rpmfusion-free.repo ]; then
	$SUDO dnf -y -q install epel-release dnf-plugins-core
	$SUDO dnf config-manager --set-enabled crb
	$SUDO dnf -y -q install https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
fi
$SUDO dnf -y -q install --allowerasing which rpm-build createrepo_c rsync wget curl unzip zip bzip2 tar perl gcc gcc-c++ make \
	systemd initscripts chkconfig byacc flex pam-devel openssl-devel zlib-devel pcre-devel \
	librdkafka-devel ffmpeg-devel mariadb-connector-c-devel expat-devel unixODBC-devel >/dev/null

# the recipes expect the repo in ~/sources/platform-install-packages, sources in ~/rpmbuild/SOURCES
# and the specs in ~/rpmbuild/SPECS (see build/sources.rc)
mkdir -p ~/sources ~/rpmbuild/SOURCES $LOGS
rsync -a --delete --exclude .git --exclude .vagrant --exclude "deb/*/repo" --exclude "rpm/*/repo" --exclude kaltura-console "$SRC/" "$WORK/"
[ -r $WORK/build/packager.rc ] || sed -e 's/@PACKAGER_NAME@/Kaltura CE/' -e 's/@PACKAGER_MAIL@/noreply@kaltura.org/' $WORK/build/packager.template.rc > $WORK/build/packager.rc
ln -sfn $WORK/RPM/SPECS ~/rpmbuild/SPECS
# .rpmmacros carries the app versions kaltura-base writes into its configs; no GPG signing here
grep -v '^%_signature\|^%_gpg_name' $WORK/RPM/.rpmmacros > ~/.rpmmacros
cp -f $WORK/RPM/SOURCES/* ~/rpmbuild/SOURCES/
set +u
. $WORK/build/sources.rc
set -u

build_one() {
	local B=$WORK/build
	case $1 in
	kaltura-postinst)	$B/package_kaltura_postinst.sh ;;
	kaltura-monit)		$B/package_kaltura_monit.sh ;;
	kaltura-base)		$B/package_kaltura_core.sh ;;
	kaltura-kmcng)		$B/package_kaltura_kmcng.sh ;;
	kaltura-html5lib)	$B/package_kaltura_html5lib.sh ;;
	kaltura-html5lib3)	$B/package_kaltura_html5lib3.sh ;;
	kaltura-html5-studio)	$B/package_kaltura_html5-studio.sh ;;
	kaltura-html5-studio3)	$B/package_kaltura_html5-studio3.sh ;;
	kaltura-nginx)		$B/package_kaltura_nginx.sh ;;
	kaltura-ffmpeg|kaltura-ffmpeg-aux)
		# EL9 bridge packages over the RPM Fusion ffmpeg
		rpmbuild -bb $WORK/rpm/el9/SPECS/$1.spec ;;
	kaltura-sphinx)
		# the googlecode SVN is gone; EL9 builds the 2.2.11 release tarball
		wget -q -N -P ~/rpmbuild/SOURCES https://sphinxsearch.com/files/sphinx-2.2.11-release.tar.gz
		echo "6662039f093314f896950519fa781bc87610f926f64b3d349229002f06ac41a9  $HOME/rpmbuild/SOURCES/sphinx-2.2.11-release.tar.gz" | sha256sum -c -
		rpmbuild -bb ~/rpmbuild/SPECS/kaltura-sphinx.spec ;;
	kaltura-html5-analytics)
		cd $SOURCE_PACKAGING_DIR
		wget -q https://github.com/kaltura/analytics-front-end/releases/download/$HTML5_APP_ANALYTICS_VERSION/kmcAnalytics_$HTML5_APP_ANALYTICS_VERSION.zip -O kmcAnalytics.zip
		rm -rf $HTML5_APP_ANALYTICS_VERSION $1-$HTML5_APP_ANALYTICS_VERSION
		unzip -q kmcAnalytics.zip && mv $HTML5_APP_ANALYTICS_VERSION $1-$HTML5_APP_ANALYTICS_VERSION
		tar zcf $RPM_SOURCES_DIR/$1-$HTML5_APP_ANALYTICS_VERSION.tar.gz $1-$HTML5_APP_ANALYTICS_VERSION
		rm -rf $1-$HTML5_APP_ANALYTICS_VERSION kmcAnalytics.zip
		rpmbuild -bb ~/rpmbuild/SPECS/$1.spec ;;
	*)			rpmbuild -bb ~/rpmbuild/SPECS/$1.spec ;;
	esac
}

mkdir -p "$REPO"
for pkg in $PACKAGES; do
	echo "===== $pkg"
	if ! (build_one $pkg) > $LOGS/$pkg.log 2>&1; then
		tail -40 $LOGS/$pkg.log
		echo "FAILED: $pkg (full log: $LOGS/$pkg.log)"
		exit 1
	fi
	# copy the binary RPMs of this package (not debuginfo/debugsource)
	find ~/rpmbuild/RPMS -name "$pkg-[0-9v]*.rpm" ! -name '*-debuginfo-*' ! -name '*-debugsource-*' -exec cp -f {} "$REPO/" \;
done

createrepo_c -q --update "$REPO"
echo "Repository: $REPO"
ls -1 "$REPO"/*.rpm

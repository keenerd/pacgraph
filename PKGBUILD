# Contributor: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20090505
pkgrel=1
pkgdesc="Draws a graph of installed packages.  Good for finding bloat."
arch=('i686' 'x86_64')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape' 'imagemagick' 'svg2png')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('ae28621fb330cdaff7149a4980a309a0')

build() {
  cd $startdir/src/$pkgname
  mkdir -p $pkgdir/usr/bin/
  cp pacgraph $pkgdir/usr/bin/
}



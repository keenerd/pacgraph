# Contributor: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20090503
pkgrel=1
pkgdesc="Draws a graph of installed packages.  Good for finding bloat."
arch=('i686' 'x86_64')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape' 'imagemagick' 'svg2png')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('64df11306d4a1869dbaff1eda5331d9e')

build() {
  cd $startdir/src/$pkgname
  mkdir -p $pkgdir/usr/sbin/
  cp pacgraph $pkgdir/usr/sbin/
}



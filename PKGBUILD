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
md5sums=('f7f8d0a12d3eeab2717c4b8ed1dbc47c')

build() {
  cd $startdir/src/$pkgname
  mkdir -p $pkgdir/usr/bin/
  cp pacgraph $pkgdir/usr/bin/
}



# Maintainer: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20110317
pkgrel=1
pkgdesc="Draws a graph of installed packages to PNG/SVG/GUI/console.  Good for finding bloat."
arch=('any')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape: png backend'
            'imagemagick: png backend'
            'svg2png: png backend'
            'tk: gui version')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('43c3a95014461dc1da1660b133676321')

build() {
  cd "$srcdir/$pkgname"
  install -D -m 0755 pacgraph    "$pkgdir/usr/bin/pacgraph"
  install -D -m 0755 pacgraph-tk "$pkgdir/usr/bin/pacgraph-tk"
}


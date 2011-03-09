# Contributor: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20110307
pkgrel=1
pkgdesc="Draws a graph of installed packages to PNG, SVG, console or GUI.  Good for finding bloat."
arch=('any')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape' 'imagemagick' 'svg2png' 'tk')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('2561e8a2e76a23a769e3330cbdfdc608')

build() {
  cd "$srcdir/$pkgname"
  install -D -m 0755 pacgraph    "$pkgdir/usr/bin/pacgraph"
  install -D -m 0755 pacgraph-tk "$pkgdir/usr/bin/pacgraph-tk"
}


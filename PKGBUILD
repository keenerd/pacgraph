# Contributor: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20090614
pkgrel=2
pkgdesc="Draws a graph of installed packages to PNG, SVG, console or GUI.  Good for finding bloat."
arch=('i686' 'x86_64')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape' 'imagemagick' 'svg2png' 'tk')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('f91d930b22a75c8900c7539d09e0fa7e')

build() {
  cd $startdir/src/$pkgname
  install -D -m 0755 pacgraph   ${pkgdir}/usr/bin/pacgraph
  install -D -m 0755 pacgraph-i ${pkgdir}/usr/bin/pacgraph-i
}


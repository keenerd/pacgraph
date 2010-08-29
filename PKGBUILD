# Contributor: Kyle Keen <keenerd@gmail.com>
pkgname=pacgraph
pkgver=20100828
pkgrel=1
pkgdesc="Draws a graph of installed packages to PNG, SVG, console or GUI.  Good for finding bloat."
arch=('any')
url="http://kmkeen.com/pacgraph/"
license=('GPL')
depends=('python')
makedepends=()
optdepends=('inkscape' 'imagemagick' 'svg2png' 'tk' 'optipng')
source=(http://kmkeen.com/pacgraph/$pkgname-$pkgver.tar.gz)
md5sums=('406459658f177b954ea4c6fc8b878c7a')

build() {
  cd $startdir/src/$pkgname
  install -D -m 0755 pacgraph   ${pkgdir}/usr/bin/pacgraph
  install -D -m 0755 pacgraph-i ${pkgdir}/usr/bin/pacgraph-i
}


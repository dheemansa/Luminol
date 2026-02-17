# Maintainer: dheemansa <dheemansa2007@gmail.com>
pkgname=luminol
_pkgname=Luminol
pkgver=0.1.0a1
pkgrel=1
pkgdesc="Color palette generator and theme exporter"
arch=('any')
url="https://github.com/dheemansa/Luminol"
license=('GPL3')
depends=('python>=3.11' 'python-pillow' 'python-numpy')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
# This PKGBUILD is configured for building directly from the git source.
# To use, run 'make local-build'.

# Remote source for publishing (uncomment to publish to AUR)
# source=("$url/archive/refs/tags/v$pkgver.tar.gz")

# Local source for building from the repository
source=("${_pkgname}-${pkgver}.tar.gz")
sha256sums=('1a89f7f9fddec53c9cb30771216a06d1ed91e8003a6b4a33978935d719d51840')

build() {
	cd "${_pkgname}-${pkgver}"
	python -m build --wheel --no-isolation
}

package() {
	cd "${_pkgname}-${pkgver}"
	python -m installer --destdir="$pkgdir" dist/${pkgname}-*.whl
}

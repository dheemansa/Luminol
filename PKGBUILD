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
sha256sums=('7684e8d38d5a8578317c62b9ea2b351f79e1ca205d1f155f311bdf652a07f2b9')

build() {
	cd "${_pkgname}-${pkgver}"
	python -m build --wheel --no-isolation
}

package() {
	cd "${_pkgname}-${pkgver}"
	python -m installer --destdir="$pkgdir" dist/${pkgname}-*.whl
}

help:
	@echo "Make targets:"
	@echo "  download-pyenv"
	@echo "  docker"
	@echo "  pyenv-docker"

download-pyenv:
	@if [ ! -e pyenv-installer ] ; then \
		curl -qsL -o pyenv-installer-$$(date +%Y%m%d).sh https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer ; \
		chmod 755 pyenv-installer-$$(date +%Y%m%d).sh ; \
		ln -sf pyenv-installer-$$(date +%Y%m%d).sh pyenv-installer ; \
	fi

docker: pyenv-docker

pyenv-docker:
	DOCKER_BUILDKIT=1 \
		BUILDKIT_PROGRESS=plain \
		docker build \
			--build-arg PYENV_INSTALL_VERSION="$$(cat ../../.python-version)" \
			-t pyenv:alpine \
			-f Dockerfile \
			.
	docker tag pyenv:alpine pyenv:alpine-3.18-python-3.9

.PHONY : build _dockerfile publish clean clean_container clean_image run join start stop devel _devel_run

IMAGE=cluster-manager
VERS=$(shell cat version.txt)
NAME=$(IMAGE)_dev
DEVDIR=$(shell pwd)
UPSTREAM=$(shell cat upstream.txt)

build: clean _build_app
_build_app:
	podman build --rm --pull -t $(UPSTREAM)/$(IMAGE):dev .

clean: clean_container clean_app_image
clean_container:
	podman container rm "$(NAME)" || :
clean_app_image:
	podman image rm -f $(UPSTREAM)/$(IMAGE):dev || :

publish:
	podman image tag $(UPSTREAM)/$(IMAGE):dev $(UPSTREAM)/$(IMAGE):$(VERS)
	podman image tag $(UPSTREAM)/$(IMAGE):dev $(UPSTREAM)/$(IMAGE):latest
	podman push $(UPSTREAM)/$(IMAGE):$(VERS)
	podman push $(UPSTREAM)/$(IMAGE):latest

publish_dev:
	podman push $(UPSTREAM)/$(IMAGE):dev

run:
	podman run --name "$(NAME)" -it $(UPSTREAM)/$(IMAGE):dev || podman start -ia "$(NAME)"

join:
	podman exec -it "$(NAME)" /bin/bash

start:
	podman start -ia "$(NAME)"

stop:
	podman stop "$(NAME)"

devel: clean_container _devel_run

_devel_run:
	podman run --name "$(NAME)" \
		--env-file ./devel.env \
		-v $(DEVDIR)/app:/app:Z -v $(DEVDIR)/data:/data:Z \
		-it $(UPSTREAM)/$(IMAGE):dev \
		/bin/bash


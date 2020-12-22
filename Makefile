.PHONY : build _build_app publish publish_dev clean clean_container clean_app_image run join start stop devel _devel_run release

IMAGE=cluster-manager
VERS=$(shell cat version.txt)
VERS_PARTIAL=$(shell awk -F. '{ print $$1"."$$2; }' version.txt)
NAME=$(IMAGE)_dev
DEVDIR=$(shell pwd)
UPSTREAM=$(shell cat upstream.txt)

build: clean_container _build_app
_build_app:
	podman build -t $(UPSTREAM)/$(IMAGE):dev .

clean: clean_container clean_app_image
clean_container:
	podman container rm "$(NAME)" || :
clean_app_image:
	podman image rm -f $(UPSTREAM)/$(IMAGE):dev || :

release:
	TMPFILE=/tmp/release-message-v$(VERS)-$$(cat /dev/urandom | head -c 32 | tr -dc _A-Z-a-z-0-9); \
	vim $$TMPFILE; \
	MSG=$$(cat $$TMPFILE | awk '{printf "%s\\n", $$0}'); \
	rm $$TMPFILE; \
	echo "{\"tag_name\": \"v$(VERS)\", \"target_commitish\": \"master\", \"name\": \"v$(VERS)\", \"body\": \"$$MSG\", \"draft\": false, \"prerelease\": false}"; \
	echo "{\"tag_name\": \"v$(VERS)\", \"target_commitish\": \"master\", \"name\": \"v$(VERS)\", \"body\": \"$$MSG\", \"draft\": false, \"prerelease\": false}" | gh api https://api.github.com/repos/:owner/:repo/releases -X POST --input /dev/stdin

publish:
	podman image tag $(UPSTREAM)/$(IMAGE):dev $(UPSTREAM)/$(IMAGE):$(VERS)
	podman image tag $(UPSTREAM)/$(IMAGE):dev $(UPSTREAM)/$(IMAGE):$(VERS_PARTIAL)
	podman image tag $(UPSTREAM)/$(IMAGE):dev $(UPSTREAM)/$(IMAGE):latest
	podman push $(UPSTREAM)/$(IMAGE):$(VERS)
	podman push $(UPSTREAM)/$(IMAGE):$(VERS_PARTIAL)
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

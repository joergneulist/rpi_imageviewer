SRVC_NAME = imvi-kiosk
LAUNCHER = $(shell readlink -f ~/.local/bin/kiosk)

.PHONY: wheel install kiosk nokiosk


wheel:
	python3 imvi/setup.py bdist_wheel


install: wheel
	pip3 install --update imvi/dist/imvi-0.1-py3-none-any.whl
	install -D -m 644 etc/config.json ~/.imvi.json
	install -D -m 755 bin/kiosk $(LAUNCHER)


kiosk: imvi.service
	sudo cp service/imvi.service /etc/systemd/system/$(SRVC_NAME).service
	systemctl enable --now $(SRVC_NAME).service

nokiosk:
	systemctl disable --now $(SRVC_NAME).service

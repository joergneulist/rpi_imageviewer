.PHONY: install kiosk nokiosk


install:
	@install -m444 etc/config/imvi.json ~/.imvi.json
	@python3 -m venv ~/imvi --clear --symlinks
	@~/imvi/bin/pip3 install .


kiosk: imvi.service
	sudo cp service/imvi.service /etc/systemd/system/$(SRVC_NAME).service
	systemctl enable --now $(SRVC_NAME).service


nokiosk:
	systemctl disable --now $(SRVC_NAME).service

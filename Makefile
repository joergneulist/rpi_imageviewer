SRVC_NAME = imvi-kiosk


.PHONY: install kiosk nokiosk


install:
	@install -m444 etc/config.json ~/.imvi.json
	@python3 -m venv ~/imvi --clear --symlinks --system-site-packages
	@~/imvi/bin/pip3 install .
	install -m755 bin/imvi ~/.local/bin/imvi


kiosk:
	@sudo cp service/imvi.service /etc/systemd/system/$(SRVC_NAME).service
	sudo systemctl enable --now $(SRVC_NAME).service


nokiosk:
	sudo systemctl disable --now $(SRVC_NAME).service


uninstall: nokiosk
	@sudo rm /etc/systemd/system/$(SRVC_NAME).service
	@rm -f ~/.imvi.json
	@rm -rf ~/imvi
	@rm -f ~/.local/bin/imvi


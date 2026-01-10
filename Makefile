.PHONY: install kiosk nokiosk uninstall


install:
	install -m444 etc/config.json ~/.imvi.json
	python3 -m venv ~/imvi --clear --symlinks --system-site-packages
	~/imvi/bin/pip3 install .


kiosk:
	sudo mkdir -p /etc/systemd/system/getty@getty1.service.d
	sudo cp service/override.conf /etc/systemd/system/getty@getty1.service.d/


nokiosk:
	sudo rm -rf /etc/systemd/system/getty@getty1.service.d


uninstall: nokiosk
	rm -f ~/.imvi.json
	rm -rf ~/imvi

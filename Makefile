.PHONY: install kiosk nokiosk uninstall

TARGET=/opt/imvi
SRVC="getty@tty1.service"


install:
	sudo install -m 777 -d $(TARGET)
	python3 -m venv $(TARGET) --clear --symlinks --system-site-packages
	install -m444 etc/imvi.json $(TARGET)
	$(TARGET)/bin/pip3 install .


kiosk:
	echo "[Service]\nType=exec\nExecStart=\nExecStart=$(TARGET)/bin/python3 -m imvi $(TARGET)/imvi.json" | sudo systemctl edit $(SRVC) --stdin


nokiosk:
	sudo systemctl revert $(SRVC)


uninstall: nokiosk
	sudo rm -f $(TARGET)


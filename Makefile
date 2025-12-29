wheel:
	python3 imvi/setup.py bdist_wheel

install:
	pip3 install imvi/dist/imvi-0.1-py3-none-any.whl
	cp etc/config.json ~/.imvi.json
	cp bin/kiosk ~/.local/bin/kiosk
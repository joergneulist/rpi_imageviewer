import ctypes
import os
from pathlib import Path
from pyudev import Context, Monitor, MonitorObserver


MEDIA_PATH = Path('/tmp/imvimedia') 


class Wrap_libc():
    def __init__(self):
        self.libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
        self.libc.mount.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p)
        self.libc.umount.argtypes = [ctypes.c_char_p]
    
    def mount(self, source, target, fstype):
        ret = self.libc.mount(str(source).encode(), str(target).encode(), b'vfat', 0, None)
        if ret < 0:
            errno = ctypes.get_errno()
            print(f'mount error {source}, {target}, {fstype}: {errno}, {os.strerror(errno)}')

    def umount(self, target):
        ret = self.libc.umount(str(target).encode())
        if ret < 0:
            errno = ctypes.get_errno()
            print(f'umount error {target}: {errno}, {os.strerror(errno)}')


class USBMediaKeeper:
    def __init__(self, cb_mount=None, cb_umount=None):
        self.mounted_devices = {}
        self.callback_mount = cb_mount
        self.callback_umount = cb_umount

        self.libc = Wrap_libc()
        
        self.monitor = Monitor.from_netlink(Context())
        self.monitor.filter_by('block')
        self.observer = MonitorObserver(self.monitor, self.udev_event)
        self.observer.start()
        


    def mount(self, uuid, dev, fs):
        self.mounted_devices[uuid] = MEDIA_PATH / uuid
        self.mounted_devices[uuid].mkdir(parents=True, exist_ok=False)
        self.libc.mount(dev, self.mounted_devices[uuid], fs)
        return self.mounted_devices[uuid]


    def umount(self, uuid):
        if not uuid in self.mounted_devices:
            print(f'UUID {uuid} not found in mounted devices')
            return
        
        self.libc.umount(self.mounted_devices[uuid])
        self.mounted_devices[uuid].rmdir()
        path = self.mounted_devices[uuid]
        del self.mounted_devices[uuid]
        return path


    def udev_event(self, action, device):
        if device.get('ID_BUS') == 'usb' and device.get('DEVTYPE') == 'partition':
            dev = device.get('DEVNAME')
            fs = device.get('ID_FS_VERSION') #TODO Translate fstype - right now we get FAT32, but need vfat for mount
            uuid = device.get('ID_PART_ENTRY_UUID')
            if action == 'add':
                print(f'USB device added: {dev} fs={fs} uuid={uuid}')
                path = self.mount(uuid, dev, fs)
                if self.callback_mount and path:
                    self.callback_mount(path)
            elif action == 'remove':
                print(f'USB device removed: {dev} fs={fs} uuid={uuid}')
                path = self.umount(uuid)
                if self.callback_umount and path:
                    self.callback_umount(path)
            else:
                print(f'USB device event {action}: {dev} fs={fs} uuid={uuid}')


if __name__ == '__main__':
    watcher = USBMediaKeeper()
    input('WAITING FOR EVENTS...')
    print('STOPPED')

import ctypes
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

    def umount(self, target):
        ret = self.libc.umount(str(target).encode())
        if ret < 0:
            errno = ctypes.get_errno()


class USBMediaKeeper:
    def __init__(self, cb_mount=None, cb_umount=None):
        self.mounted_devices = {}
        self.callback_mount = cb_mount
        self.callback_umount = cb_umount

        self.libc = Wrap_libc()
        
        context = Context()
        # install observer
        self.monitor = Monitor.from_netlink(context)
        self.monitor.filter_by('block')
        self.observer = MonitorObserver(self.monitor, self.udev_event)
        self.observer.start()
        
        # find already existing devices
        for device in context.list_devices(subsystem='block', DEVTYPE='partition'):
            self.udev_event('add', device)
    
    def __str__(self):
        return f'{str(type(self))}: currently mounted: ' +  ', '.join([f'{uuid}@{path}' for uuid, path in self.mounted_devices.items()])

    def mount(self, uuid, dev, fs):
        self.mounted_devices[uuid] = MEDIA_PATH / uuid
        self.mounted_devices[uuid].mkdir(parents=True, exist_ok=False)
        self.libc.mount(dev, self.mounted_devices[uuid], fs)
        return self.mounted_devices[uuid]

    def umount(self, uuid):
        if uuid not in self.mounted_devices:
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
                path = self.mount(uuid, dev, fs)
                if self.callback_mount and path:
                    self.callback_mount(path)
            elif action == 'remove':
                path = self.umount(uuid)
                if self.callback_umount and path:
                    self.callback_umount(path)


if __name__ == '__main__':
    watcher = USBMediaKeeper()
    input('WAITING FOR EVENTS...')

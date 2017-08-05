import objc
import time

start = time.time()

objc.loadBundle('CoreWLAN',
                bundle_path = '/System/Library/Frameworks/CoreWLAN.framework',
                module_globals = globals())
iface = CWInterface.interface()
networks, error = iface.scanForNetworksWithName_error_('UCSD-GUEST', None)
network = networks.anyObject()
success, error = iface.associateToNetwork_password_error_(network, '', None)
end = time.time()

print end-start
#!/usr/bin/env python

from gi.repository import Gtk
import notify2
import sys

# Ubuntu's notify-osd doesn't officially support actions. However, it does have
# a dialog fallback which we can use for this demonstration. In real use, please
# respect the capabilities the notification server reports!
OVERRIDE_NO_ACTIONS = True

def default_cb(n, action):
    assert action == "default"
    print("You clicked the default action")
    n.close()

def closed_cb(n):
    print("Notification closed")

if __name__ == '__main__':
    if not notify2.init("Default Action Test", mainloop='glib'):
        sys.exit(1)

    server_capabilities = notify2.get_server_caps()

    n = notify2.Notification("Matt is online")
    n.set_category("presence.online")
    if ('actions' in server_capabilities) or OVERRIDE_NO_ACTIONS:
        n.add_action("default", "Default Action", default_cb)
    n.connect('closed', closed_cb)

    if not n.show():
        print("Failed to send notification")
        sys.exit(1)

    Gtk.main()

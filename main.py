import watch
import axp202c

w = watch.Watch()

if not w.axp.isVBUSPlug():
    # We don't want the watch connecting to everything just because we've plugged it in
    w.main()

w.charging()

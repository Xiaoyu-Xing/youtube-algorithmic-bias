import logging
import time

from pyvirtualdisplay import Display

log = logging.getLogger(__name__)


class VirtualScreen:
    def __init__(self, visible=0, size=(1920, 1080)):
        """
        Init an instance of virtual display
        :param visible: whether visible on screen, 0 for false, 1 for true
        :param size: virtual display size in pixels, as tuple form: (width, height)
        """
        self.display = Display(visible=visible, size=size)
        log.info("Virtual display set up, visible: {}, size: {}".
                      format(False if not visible else True, size))
        self.display.start()
        time.sleep(1)

    def __enter__(self):
        log.info("Created virtual display instance.")
        return self.display

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.display:
            self.display.stop()
            log.info("Virtual display stopped.")
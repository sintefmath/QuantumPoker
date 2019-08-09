# Copyright SINTEF 2019
# Authors: Franz G. Fuchs <franzgeorgfuchs@gmail.com>,
#          Christian Johnsen <christian.johnsen97@gmail.com>,
#          Vemund Falch <vemfal@gmail.com>

from matplotlib.widgets import AxesWidget

class Button(AxesWidget):
    """
    A GUI neutral button.

    For the button to remain responsive you must keep a reference to it.
    Call :meth:`on_clicked` to connect to the button.

    Attributes
    ----------
    ax
        The :class:`matplotlib.axes.Axes` the button renders into.
    label
        A :class:`matplotlib.text.Text` instance.
    color
        The color of the button when not hovering.
    hovercolor
        The color of the button when hovering.
    """

    def __init__(self, ax, label, image=None,
                 color='0.85', hovercolor='0.95'):
        """
        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The :class:`matplotlib.axes.Axes` instance the button
            will be placed into.

        label : str
            The button text. Accepts string.

        image : array, mpl image, Pillow Image
            The image to place in the button, if not *None*.
            Can be any legal arg to imshow (numpy array,
            matplotlib Image instance, or Pillow Image).

        color : color
            The color of the button when not activated

        hovercolor : color
            The color of the button when the mouse is over it
        """
        AxesWidget.__init__(self, ax)

        if image is not None:
            ax.imshow(image)
        self.label = ax.text(0.5, 0.5, label,
                             verticalalignment='center',
                             horizontalalignment='center',
                             transform=ax.transAxes, fontsize=13)

        self.cnt = 0
        self.observers = {}

        self.connect_event('button_press_event', self._click)
        self.connect_event('button_release_event', self._release)
        #self.connect_event('motion_notify_event', self._motion)
        ax.set_navigate(False)
        ax.set_facecolor(color)
        ax.set_xticks([])
        ax.set_yticks([])
        self.isIterating = False
        self.deleteFunc = None
        self.color = color
        self.hovercolor = hovercolor

        self._lastcolor = color

    def _click(self, event):
        if self.ignore(event):
            return
        if event.inaxes != self.ax:
            return
        if not self.eventson:
            return
        if event.canvas.mouse_grabber != self.ax:
            event.canvas.grab_mouse(self.ax)

    def _release(self, event):
        if self.ignore(event):
            return
        if event.canvas.mouse_grabber != self.ax:
            return
        event.canvas.release_mouse(self.ax)
        if not self.eventson:
            return
        if event.inaxes != self.ax:
            return
        self.isIterating = True
        for cid, func in self.observers.items():
            func(event)
        self.isIterating = False
        if self.deleteFunc is not None:
            del self.observers[self.deleteFunc]
            self.deleteFunc = None

    def _motion(self, event):
        if self.ignore(event):
            return
        if event.inaxes == self.ax:
            c = self.hovercolor
        else:
            c = self.color
        if c != self._lastcolor:
            self.ax.set_facecolor(c)
            self._lastcolor = c
            if self.drawon:
                self.ax.figure.canvas.draw()

    def on_clicked(self, func):
        """
        Connect the callback function *func* to button click events.

        Returns a connection id, which can be used to disconnect the callback.
        """
        cid = self.cnt
        self.observers[cid] = func
        self.cnt += 1
        return cid

    def disconnect(self, cid):
        """Remove the callback function with connection id *cid*."""
        if not(self.isIterating):
            try:
                del self.observers[cid]
            except KeyError:
                pass
        else:
            self.deleteFunc = cid
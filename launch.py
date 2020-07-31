import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
import socket
import os
import airshare
import qrcode

scriptDirectory = os.path.dirname(os.path.realpath(__file__))
logopath = scriptDirectory+'/assets/Airshare.svg'
downloadImage = scriptDirectory+'/assets/arrow-down-circle.svg'
temppath = scriptDirectory+'/tmp/temp.png'

def get_url():
    'Create url with IP for QR code'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return 'http://'+IP+':8000/'

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        '''
        Setup main window
        '''
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        self.serverState = 'stopped'
        self.filepath = None
        self.set_icon_from_file(logopath)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        vbox.set_margin_top(20)
        vbox.set_margin_start(100)
        vbox.set_margin_end(100)
        vbox.set_margin_bottom(20)
        self.add(vbox)

        serverLabel = Gtk.Label(label='Name for your computer:')
        self.serverName = Gtk.Entry()
        self.serverName.set_text(socket.gethostname())

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        self.start_btn = Gtk.Button(label='Start')
        self.start_btn.set_property("width-request", 85)
        self.start_btn.connect('clicked', self.on_start_pressed)

        self.picker_btn = Gtk.Button(label='Choose file')
        self.picker_btn.set_property("width-request", 85)
        self.picker_btn.connect('clicked', self.on_picker_btn)

        send_label = Gtk.Label()
        send_label.set_text("Pick file to send:")

        sendbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        sendbox.add(send_label)
        sendbox.add(self.picker_btn)

        # Create switch at top for send/receive
        self.stack.add_titled(sendbox, "send", "Send")

        #receive_label = Gtk.Label(label='Receive')
        receive_label = Gtk.Image()
        receive_label.set_from_file(downloadImage)
        self.stack.add_titled(receive_label, "receive", "Receive")

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.props.halign = Gtk.Align.CENTER
        stack_switcher.set_stack(self.stack)

        # Image at bottom initiated as logo then changed to QR code later
        self.img = Gtk.Image()
        self.img.set_from_file(logopath)

        self.showURL = Gtk.Label()
        self.showURL.set_line_wrap(True)

        vbox.pack_start(stack_switcher, False, True, 0)
        vbox.pack_start(self.stack, False, False, 0)
        vbox.pack_start(serverLabel, False, False, 0)
        vbox.pack_start(self.serverName, False, False, 0)
        vbox.pack_start(self.img, True, True, 0)
        vbox.pack_start(self.showURL, True, True, 0)
        vbox.pack_start(self.start_btn, False, False, 10)

    def on_picker_btn(self, widget):
        'Loads file picker window (built into GTK)'
        dlg = Gtk.FileChooserDialog(title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN)
        dlg.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        response = dlg.run()
        if response == Gtk.ResponseType.OK:
            self.filepath = dlg.get_filename()
            self.picker_btn.set_label(os.path.basename(self.filepath))
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dlg.destroy()

    def inactivate_buttons(self):
        'Changes buttons when server started'
        self.picker_btn.set_sensitive(False)
        self.start_btn.set_label('Stop')

    def activate_buttons(self):
        'Resets buttons'
        self.picker_btn.set_sensitive(True)
        self.start_btn.set_label('Start')
        self.showURL.set_text('')

    def updateURLLabel(self):
        '''
        Creates two URLs
        One for QR
        One which uses selected local DNS hostname
        '''
        self.url = get_url()
        urlText = "Go to 'http://{0}.local:8000' on your web browser or scan QR code".format(self.serverName.get_text())
        self.showURL.set_text(urlText)

    def makeQRcode(self):
        'Use qrcode module create image file'
        # Of note, Airshare module does this on its own but
        # just prints it to stdout
        # could submit upstream support for saving to temp file or something
        # but recreating was just easier
        qr = qrcode.QRCode(version=1, box_size=5)
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#9900cc', back_color='white')
        img.save(temppath)

    def on_start_pressed(self, widget):
        'Start button action'
        if self.serverState == 'running':
            self.process.terminate()
            self.serverState = 'stopped'
            self.activate_buttons()
            self.img.set_from_file(logopath)
        elif self.serverState == 'stopped':
            selected = self.stack.get_visible_child_name()
            if selected == 'send':
                if self.filepath is not None:
                    self.inactivate_buttons()
                    self.updateURLLabel()
                    self.send_file_start()
                    self.serverState = 'running'
                else:
                    self.showURL.set_text('Please select a file')
            elif selected == 'receive':
                self.inactivate_buttons()
                self.updateURLLabel()
                self.receive_file_start()
                self.serverState = 'running'

    def send_file_start(self):
        'Start send file server'
        self.process = airshare.sender.send_server_proc(code=self.serverName.get_text(), file=self.filepath)
        self.makeQRcode()
        self.img.set_from_file(temppath)
        try:
            self.process.start()
        except airshare.exception.CodeExistsError as cee:
            pass
        except Exception as e:
            print(e)


    def receive_file_start(self):
        'Start receive server'
        self.process = airshare.receiver.receive_server_proc(code=self.serverName.get_text())
        self.makeQRcode()
        self.img.set_from_file(temppath)
        try:
            self.process.start()
        except airshare.exception.CodeExistsError as e:
            pass
        except Exception as e:
            print(e)

    def _shutdown_(self):
        'Do not want any to leave any running processes'
        try:
            self.process.terminate()
        except Exception as e:
            pass


def on_activate(app):
    global window
    window = MainWindow(application=app, title='Airshare')
    window.show_all()
    window.set_position(Gtk.WindowPosition.CENTER)

app = Gtk.Application(application_id='com.pangwalla.airshareWidget')
app.connect('activate', on_activate)

try:
    app.run(None)
except Exception as e:
    print(e)
finally:
    window._shutdown_()

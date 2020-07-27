import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
import socket
import os
import airshare
import qrcode

logopath = 'assets/Airshare.svg'
temppath = 'tmp/temp.png'

def get_url():
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
        Gtk.ApplicationWindow.__init__(self, *args, **kwargs)
        self.serverState = 'stopped'
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
        #
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)
        #
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

        self.stack.add_titled(sendbox, "send", "Send")
        #
        receive_label = Gtk.Label(label='Receive')
        self.stack.add_titled(receive_label, "receive", "Receive")
        #
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.props.halign = Gtk.Align.CENTER
        stack_switcher.set_stack(self.stack)

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
        self.picker_btn.set_sensitive(False)
        self.start_btn.set_label('Stop')

    def activate_buttons(self):
        self.picker_btn.set_sensitive(True)
        self.start_btn.set_label('Start')
        self.showURL.set_text('')

    def updateURLLabel(self):
        IP = airshare.utils.get_local_ip_address()
        self.url = get_url()
        urlText = "Go to 'http://{0}.local:8000' on your web browser or scan QR code".format(self.serverName.get_text())
        self.showURL.set_text(urlText)

    def makeQRcode(self):
        qr = qrcode.QRCode(version=1, box_size=5)
        qr.add_data(self.url)
        qr.make(fit=True)
        img = qr.make_image(fill_color='#9900cc', back_color='white')
        #qrCode = qrcode.make(self.url)
        img.save(temppath)

    def on_start_pressed(self, widget):
        if self.serverState == 'running':
            self.process.terminate()
            self.serverState = 'stopped'
            self.activate_buttons()
            self.img.set_from_file(logopath)
        elif self.serverState == 'stopped':
            selected = self.stack.get_visible_child_name()
            self.inactivate_buttons()
            self.updateURLLabel()
            if selected == 'send':
                self.send_file_start()
            elif selected == 'receive':
                self.receive_file_start()
            self.serverState = 'running'

    def send_file_start(self):
        print(self.serverName.get_text())
        if self.filepath is not None:
            self.process = airshare.sender.send_server_proc(code=self.serverName.get_text(), file=self.filepath)
            self.img.set_from_file(temppath)
            try:
                    self.process.start()
            except airshare.exception.CodeExistsError as cee:
                pass
            except Exception as e:
                print(e)
        else:
            self.showURL.set_text('Please select a file')

    def receive_file_start(self):
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
        try:
            self.process.terminate()
        except Exception as e:
            pass



def on_activate(app):
    global win
    win = MainWindow(application=app, title='Airshare')
    win.show_all()

app = Gtk.Application(application_id='com.clow.airshareWidget')
app.connect('activate', on_activate)

try:
    app.run(None)
except Exception as e:
    print(e)
finally:
    win._shutdown_()

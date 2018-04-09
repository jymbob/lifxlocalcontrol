import logging
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from apscheduler.schedulers.background import BackgroundScheduler
from lifxlan import LifxLAN, Light, Group

PORT = 7990
NUM_LIGHTS = 10
LIGHTS = {}

sched = BackgroundScheduler()
sched.start()


class S(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.devices = LifxLAN(NUM_LIGHTS)
        sched.add_job(self.get_lights,
                      'interval',
                      minutes=2,
                      id='get_lights',
                      replace_existing=True)
        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def get_lights(self):

        lights = self.devices.get_lights()
        resp = "<table><tbody>"
        for l in lights:
            LIGHTS[l.get_label()] = {'mac': l.get_mac_addr(),
                                     'ip': l.get_ip_addr(),
                                     'colour': l.get_color()}
            resp += "<tr><td>" + l.get_label() + "</td>"
            resp += "<td>{}</td>".format(l.get_color())
            resp += "<td>" + l.get_mac_addr() + "</td>"
            resp += "<td>" + l.get_ip_addr() + "</td></tr>"

        resp += '</tbody></table>'
        resp += "<p>POST to /lights with either mac&ip or light (with label)<br/>"
        resp += "no args: toggle on/off<br/>"
        resp += "<pre>level</pre> 'on'/'off', or 0/65535<br/>"
        resp += "<pre>dim</pre> 'up'/'down' or no arg to continue last dim (1/10th each time)<br/>"
        resp += "<pre>white</pre> 'warm'/'cool' to change kelvin level</p>"
        logging.debug(len(LIGHTS))
        return resp

    def set_lights(self, postvars={}):
        sched.pause()
        resp = 'no post data found'
        l = None
        if any(postvars):
            resp = 'vars!'
            mac = postvars.get('mac', None)
            if mac:
                ip = postvars.get('ip', None)
                if ip:
                    l = Light(mac[0], ip[0])
            light = postvars.get('light', None)
            if light:
                logging.debug(light)
                if light[0] in LIGHTS:
                    logging.debug('found {}'.format(light[0]))
                    light = LIGHTS.get(light[0])
                    mac = light.get('mac')
                    ip = light.get('ip')
                    colour = light.get('colour')
                    l = Light(mac, ip)
                else:
                    logging.debug(LIGHTS)
                    l = self.devices.get_device_by_name(light[0])
                    if l:
                        colour = l.get_color()

            if l:
                level = postvars.get('level', None)
                dim = postvars.get('dim', None)
                white = postvars.get('white', None)
                if level is not None:
                    try:
                        if (level[0] == 'full'):
                            h, s, b, k = colour
                            b = 65535
                            l.set_power('on')
                            l.set_color([h, s, b, k], 300)
                        else:
                            l.set_power(level[0])
                            resp = 'set power {}'.format(level)
                    except Exception as e:
                        resp = 'err... {}'.format(repr(e))
                elif dim is not None:
                    switch_after_dim = False
                    try:
                        h, s, b, k = colour
                        if l.get_power() == 0:
                            switch_after_dim = True
                            b = 0
                        dim = dim[0]
                        if dim not in ('up', 'down'):
                            dim = LIGHTS[l.get_label()].get('last_dim', None)
                            if dim is None or b in (0, 65535):
                                if b > 32000:
                                    dim = 'down'
                                else:
                                    dim = 'up'
                        if dim == 'down':
                            b -= 6554
                        if dim == 'up':
                            b += 6554
                        if b < 0:
                            b = 0
                        if b > 65535:
                            b = 65535
                        l.set_color([h, s, b, k], 600)
                        if LIGHTS.get(l.get_label(), None) is None:
                            LIGHTS[l.get_label()] = {'mac': l.get_mac_addr(),
                                                     'ip': l.get_ip_addr(),
                                                     'colour': l.get_color(),
                                                     'last_dim': dim}
                        else:
                            LIGHTS[l.get_label()]['colour'] = [h, s, b, k]
                            LIGHTS[l.get_label()]['last_dim'] = dim
                        if switch_after_dim is True:
                            l.set_power('on')
                        resp = 'set brightness {}'.format(b)
                    except Exception as e:
                        resp = 'dim... {}'.format(repr(e))
                elif white is not None:
                    try:
                        h, s, b, k = colour
                        white = white[0]
                        if white not in ('warm', 'cool'):
                            k = int(white)
                        if white == 'warm':
                            k -= 500
                        if white == 'cool':
                            k += 500
                        if k < 2500:
                            k = 2500
                        if k > 9000:
                            k = 9000
                        l.set_color([h, s, b, k], 500)
                        if LIGHTS.get(l.get_label(), None) is None:
                            LIGHTS[l.get_label()] = {'mac': l.get_mac_addr(),
                                                     'ip': l.get_ip_addr(),
                                                     'colour': l.get_color()}
                        else:
                            LIGHTS[l.get_label()]['colour'] = [h, s, b, k]
                        resp = 'set white level {}'.format(k)
                    except Exception as e:
                        resp = 'white... {}'.format(repr(e))

                else:
                    try:
                        if l.get_power() > 0:
                            l.set_power(0)
                        else:
                            l.set_power('on')
                    except:
                        resp = 'nope...'
            else:
                resp = "<p>Light not found ):</p>"
        sched.resume()
        return resp

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>Hi!</h1><p>Path: {path}</p>".format(path=self.path))

        if self.path == '/lights':
            self.wfile.write(self.get_lights())

        self.wfile.write("</body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        if len(postvars):
            i = 0
            for key in sorted(postvars):
                logging.debug('ARG[%d] %s=%s' % (i, key, postvars[key]))
                i += 1

        self._set_headers()
        self.wfile.write("<html><body><p>POST</p>")
        logging.debug(self.headers)
        if self.path.startswith('/lights'):
            self.wfile.write(self.set_lights(postvars))

        self.wfile.write("</body></html>")


def run(server_class=HTTPServer, handler_class=S, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print "Starting httpd..."
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.DEBUG)
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

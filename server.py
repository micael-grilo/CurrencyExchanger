from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sqlite3, cgi, json

conn = sqlite3.connect('currencies.db')

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        message = "Welcome!"
        self.wfile.write(bytes(message, "utf8"))
        return

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        #Gets POST parameters
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_url = urlparse('?'+(post_data.decode('utf8')))
        params = parse_qs(parsed_url.query)

        base_curr_param = params['bcurr'][0]
        target_curr_param = params['tcurr'][0]
        from_timestamp_param = params['df'][0]
        to_timestamp_param = params['dt'][0]
        amount_param = params['am'][0]

        result = {}
        c = conn.cursor()
        c.execute("""SELECT TIMESTAMP, RATES FROM exchangeRates WHERE TIMESTAMP BETWEEN ? AND ? """, (from_timestamp_param, to_timestamp_param,))
        for line in c.fetchall():
            timestamp = line[0]
            currency_json = json.loads(line[1].replace("'", "\""))
            converted_amount = (float(amount_param) / currency_json[base_curr_param]) * currency_json[target_curr_param]
            result.update({timestamp : converted_amount})

        self.wfile.write(bytes(str(result), "utf8"))
        return

def run():
    print('starting server...')
    server_address = ('127.0.0.1', 8084)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()


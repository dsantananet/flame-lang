import io
import os
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import meteo_server as server

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.base = 'http://127.0.0.1:' + str(cls.http.server_port)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close(); cls.thread.join()

    def test_dashboard(self):
        with urllib.request.urlopen(self.base + '/web/meteo/') as r:
            self.assertIn(b'Meteo', r.read())

    def test_missing_key(self):
        with patch.dict(os.environ, {'WU_API_KEY':''}):
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(self.base + '/api/wu')
            self.assertEqual(ctx.exception.code, 503)

    def test_key_never_appears_in_errors(self):
        server.CACHE = None
        with patch.dict(os.environ, {'WU_API_KEY':'SECRET-TEST'}):
            with patch.object(server.urllib.request, 'urlopen', side_effect=RuntimeError('SECRET-TEST')):
                request = urllib.request.Request(self.base + '/api/wu')
                # Use a separate HTTP client so the upstream mock does not replace our client.
                import http.client
                c = http.client.HTTPConnection('127.0.0.1', self.http.server_port)
                c.request('GET', '/api/wu'); r = c.getresponse()
                self.assertEqual(r.status, 502)
                self.assertNotIn(b'SECRET-TEST', r.read()); c.close()

    def test_private_paths(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(self.base + '/.git/config')
        self.assertEqual(ctx.exception.code, 403)

    def test_wu_station_units_and_daily_rain_not_mislabeled(self):
        rows=server.wu_rows({'observations':[{'stationID':'IALDEI10','obsTimeUtc':'2026-01-01T12:00:00Z','lat':40,'lon':-7,'humidity':0,'metric':{'temp':15,'windSpeed':10,'precipTotal':25}}]})
        self.assertEqual(rows[0]['temperature'],15)
        self.assertEqual(rows[0]['humidity'],0)
        self.assertIsNone(rows[0]['rain'])

if __name__ == '__main__': unittest.main()

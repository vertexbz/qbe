import http.client
import json
from urllib.parse import urlparse, quote


class MoonrakerAPI:
    def __init__(self, api_url: str):
        self.api_url = urlparse(api_url)

    def _req(self, method: str, url: str) -> dict:
        https = self.api_url.scheme == 'https'
        hostname = self.api_url.hostname
        port = self.api_url.port or (443 if https else 80)

        if https:
            conn = http.client.HTTPSConnection(hostname, port)
        else:
            conn = http.client.HTTPConnection(hostname, port)

        conn.request(method, url, headers={"Host": hostname})
        response = conn.getresponse()
        content = response.read()

        if response.status != 200:
            raise BrokenPipeError('api request error: ' + content.decode('utf-8'))
        return json.loads(content).get('result')

    def list_mcus(self) -> list[str]:
        return list(filter(lambda s: s.startswith('mcu'), self._req('GET', '/printer/objects/list').get('objects')))

    def get_mcu_klipper_version(self, *mcus: str) -> dict[str, str]:
        if len(mcus) == 0:
            raise ValueError('must provide at least one mcu')
        mcus = map(lambda m: quote(m) + '=mcu_version', mcus)
        result = self._req('GET', '/printer/objects/query?' + '&'.join(mcus)).get('status')

        for key in result.keys():
            result[key] = result[key].get('mcu_version')

        return result

    def get_all_mcus_klipper_version(self):
        return self.get_mcu_klipper_version(*self.list_mcus())

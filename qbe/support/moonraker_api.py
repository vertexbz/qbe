import http.client
import json
from typing import Any, Union
from urllib.parse import urlparse, quote


class MoonrakerAPI:
    def __init__(self, api_url: str):
        self.api_url = urlparse(api_url)

    def _req(self, method: str, url: str, body: Union[str, None] = None) -> dict:
        https = self.api_url.scheme == 'https'
        hostname = self.api_url.hostname
        port = self.api_url.port or (443 if https else 80)

        if https:
            conn = http.client.HTTPSConnection(hostname, port)
        else:
            conn = http.client.HTTPConnection(hostname, port)

        conn.request(method, url, body, headers={"Host": hostname, "Content-type": "application/json"})
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

    def set_namespace_value(self, namespace: str, key: str, value: Any):
        payload = {"namespace": namespace, "key": key, "value": value}
        self._req('POST', '/server/database/item?namespace=' + namespace + '&key=' + key, json.dumps(payload))

    def set_namespace(self, namespace: str, values: dict[str, Any]):
        for key, value in values.items():
            self.set_namespace_value(namespace, key, value)

    def get_namespace_value(self, namespace: str, key: str):
        return self._req('GET', '/server/database/item?namespace=' + namespace + '&key=' + key) \
            .get('result').get('value')

    def get_namespace(self, namespace: str):
        return self._req('GET', '/server/database/item?namespace=' + namespace) \
            .get('result').get('value')

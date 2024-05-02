from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional, Tuple, Union

import requests


class FetchError(Exception):
    pass


class FetchNetworkError(FetchError):
    pass


class FetchHTTPError(FetchError):
    def __init__(self, response: requests.Response, *args):
        super().__init__(*args)
        self.request: requests.PreparedRequest = response.request
        self.response: requests.Response = response


class FetchHTTPClientError(FetchHTTPError):  # 4xx
    pass


class FetchHTTPServerError(FetchHTTPError):  # 5xx
    pass


async def request(
    method: str,
    url: str,
    params: Optional[Union[Dict[str, Any], Tuple[str, ...], bytes]] = None,
    data: Optional[Union[Dict[str, Any], Tuple[str, ...], bytes]] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str], requests] = None,
    files: Optional[Dict[str, Union[Any, Tuple[str, Any, str, Dict[str, str]]]]] = None,
    auth: Optional[Tuple[str, str]] = None,
    timeout: Union[float, Tuple[float, float]] = None,
    allow_redirects: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    verify: Union[bool, str] = True,
    stream: bool = False,
    cert: Optional[Union[str, Tuple[str, str]]] = None
):
    def fetch():
        return requests.request(
            method, url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            files=files,
            auth=auth,
            timeout=timeout,
            allow_redirects=allow_redirects,
            proxies=proxies,
            verify=verify,
            stream=stream,
            cert=cert,
        )

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, fetch)

    if response.status_code >= 600:
        raise FetchHTTPError(response, response.reason)
    if response.status_code >= 500:
        raise FetchHTTPServerError(response, response.reason)
    if response.status_code >= 400:
        raise FetchHTTPClientError(response, response.reason)

    return response


async def get(
    url: str,
    params: Optional[Union[Dict[str, Any], Tuple[str, ...], bytes]] = None,
    data: Optional[Union[Dict[str, Any], Tuple[str, ...], bytes]] = None,
    json: Optional[Any] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    files: Optional[Dict[str, Union[Any, Tuple[str, Any, str, Dict[str, str]]]]] = None,
    auth: Optional[Tuple[str, str]] = None,
    timeout: Union[float, Tuple[float, float]] = None,
    allow_redirects: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    verify: Union[bool, str] = True,
    stream: bool = False,
    cert: Optional[Union[str, Tuple[str, str]]] = None
):
    return await request(
        'GET', url,
        params=params,
        data=data,
        json=json,
        headers=headers,
        cookies=cookies,
        files=files,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        proxies=proxies,
        verify=verify,
        stream=stream,
        cert=cert,
    )

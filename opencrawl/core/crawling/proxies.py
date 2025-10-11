import logging
import random
import urllib.request

from .structures import Proxy

logger = logging.getLogger(__name__)


class Proxies:
    def __init__(self, proxies: str):
        self._proxies = proxies
        self._proxy_list = self._load_proxies()
        if self._proxy_list:
            self._check_proxies()

    def _load_proxies(self) -> list[Proxy]:
        """Load proxies from a file or a string."""
        if not self._proxies:
            return []

        if "/" in self._proxies:
            with open(self._proxies, "r") as f:
                return [
                    Proxy(proxy.strip()) 
                    for proxy in f.read().splitlines() 
                    if proxy.strip() and not proxy.strip().startswith("#")
                ]
        else:
            return [Proxy(proxy.strip()) for proxy in self._proxies.split(",") if proxy.strip()]

    def _check_proxies(self) -> None:
        """Check if proxies are valid."""
        logger.info(f"Checking {len(self._proxy_list)} proxies...")
        
        for proxy in self._proxy_list:
            try:
                # Create proxy handler for urllib
                proxy_handler = urllib.request.ProxyHandler({
                    'http': proxy.url,
                    'https': proxy.url,
                })
                opener = urllib.request.build_opener(proxy_handler)
                
                # Test the proxy with a simple request
                opener.open("http://httpbin.org/ip", timeout=5)
                logger.info(f"Proxy OK: {proxy.url}")
                
            except Exception as e:
                logger.warning(f"Proxy check failed for {proxy.url}: {e}")

    def rotate_proxy(self) -> Proxy:
        """Rotate to the next proxy."""
        if not self._proxy_list:
            return Proxy("")
        return random.choice(self._proxy_list)

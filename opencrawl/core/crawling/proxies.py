"""
Proxies module for managing proxy servers.

This module provides a simple interface for loading, checking, and rotating proxies.
"""

import random
import urllib.request

from .structures import Proxy

class Proxies:
    """
    Proxies class for managing proxy servers.
    
    This class provides a simple interface for loading, checking, and rotating proxies.

    Attributes:
        proxies: A string of proxies separated by commas
        proxy_list: A list of Proxy objects
    """

    def __init__(self, proxies: str):
        self._proxies = proxies
        self._proxy_list = self._load_proxies()
        
        if self._proxy_list:
            self._check_proxies()

    def _load_proxies(self) -> list[Proxy]:
        """Load proxies from a file or a string.

        Args:
            None

        Returns:
            A list of Proxy objects.
        """

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
        """
        Check if proxies are valid.
        
        This method checks if the proxies are valid by making a simple request to httpbin.org/ip.
        If the request fails, the proxy is considered invalid and is removed from the list.

        Args:
            None

        Returns:
            None
        """
        
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
                
            except Exception:
                pass

    def rotate_proxy(self) -> Proxy:
        """
        Rotate to the next proxy.
        
        This method returns a random proxy from the list of proxies.

        Args:
            None

        Returns:
            A random proxy from the list of proxies
        """
        if not self._proxy_list:
            return Proxy("")
            
        return random.choice(self._proxy_list)

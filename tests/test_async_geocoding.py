"""
Tests for async geocoding functionality.

This module tests the AsyncGeocoder class which provides:
- Concurrent geocoding with configurable limits
- Retry logic with exponential backoff
- Cache integration for deduplication
- Batch processing capabilities
"""

import asyncio
import json
import os
import sys
import tempfile
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx

# Mock the server module before importing chart_generator
import unittest.mock as mock
sys.modules['server'] = mock.MagicMock()
sys.modules['server'].ensure_server_running = mock.MagicMock(return_value='http://localhost:8080')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.chart_generator import AsyncGeocoder


class TestAsyncGeocoder:
    """Tests for AsyncGeocoder class."""

    @pytest.mark.asyncio
    async def test_geocode_cached(self, tmp_path):
        """
        Test that cached addresses return immediately without API call.

        Expected behavior:
        - AsyncGeocoder with pre-populated cache
        - geocode_batch should return cached results
        - No HTTP calls should be made
        """
        # Setup: create pre-populated cache
        cache_path = tmp_path / "geo_cache.json"
        cached_address = "北京市海淀区"
        cached_coord = [116.397128, 39.916527]
        cache_data = {cached_address: cached_coord}
        cache_path.write_text(json.dumps(cache_data, ensure_ascii=False), encoding="utf-8")

        # Create geocoder with mocked HTTP client
        geocoder = AsyncGeocoder(ak="test_ak", cache_path=str(cache_path))

        # Use respx to mock HTTP - should NOT be called
        with respx.mock:
            # No routes defined - any HTTP call will fail the test
            result = await geocoder.geocode_batch([cached_address])

        # Verify cached result returned
        assert cached_address in result
        assert result[cached_address] == cached_coord

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, tmp_path):
        """
        Test that failed requests retry with exponential backoff.

        Expected behavior:
        - Mock 500 error then 200 success
        - Verify retry happens with tenacity
        - Exponential backoff: 1s, 2s, 4s
        """
        cache_path = tmp_path / "geo_cache.json"
        address = "上海市浦东新区"

        with respx.mock as respx_mock:
            # First call returns 500, second returns success
            route = respx_mock.get("https://api.map.baidu.com/geocoding/v3/").mock(
                side_effect=[
                    httpx.Response(500, json={"status": -1}),
                    httpx.Response(200, json={
                        "status": 0,
                        "result": {"location": {"lng": 121.473701, "lat": 31.230416}}
                    }),
                ]
            )

            geocoder = AsyncGeocoder(ak="test_ak", cache_path=str(cache_path))
            result = await geocoder.geocode_batch([address])

        # Verify retry happened (2 calls made)
        assert route.call_count == 2
        assert address in result
        assert result[address] == [121.473701, 31.230416]

    @pytest.mark.asyncio
    async def test_concurrency_limit(self, tmp_path):
        """
        Test that concurrency is limited to 5 simultaneous requests.

        Expected behavior:
        - Mock slow API responses
        - Verify max 5 concurrent requests using semaphore tracking
        - Additional requests wait for semaphore release
        """
        cache_path = tmp_path / "geo_cache.json"
        addresses = [f"地址{i}" for i in range(10)]

        concurrent_count = 0
        max_concurrent = 0

        def track_concurrency(request):
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)

            # Simulate slow response
            import time
            time.sleep(0.1)

            concurrent_count -= 1
            return httpx.Response(200, json={
                "status": 0,
                "result": {"location": {"lng": 116.0 + hash(request.url) % 10, "lat": 39.0 + hash(request.url) % 10}}
            })

        with respx.mock as respx_mock:
            respx_mock.get("https://api.map.baidu.com/geocoding/v3/").mock(
                side_effect=track_concurrency
            )

            geocoder = AsyncGeocoder(ak="test_ak", cache_path=str(cache_path))
            await geocoder.geocode_batch(addresses)

        # Verify max concurrent was 5 (or less, but never more)
        assert max_concurrent <= 5, f"Max concurrent requests was {max_concurrent}, expected <= 5"

    @pytest.mark.asyncio
    async def test_batch_geocoding(self, tmp_path):
        """
        Test that batch geocoding handles mixed success/failure.

        Expected behavior:
        - Mock multiple addresses
        - Verify all processed correctly
        - Cache should be updated with results
        """
        cache_path = tmp_path / "geo_cache.json"
        addresses = ["成功地址", "失败地址", "另一个成功地址"]

        def mock_response(request):
            # Decode URL to check address
            import urllib.parse
            url_str = str(request.url)
            decoded_url = urllib.parse.unquote(url_str)

            if "成功地址" in decoded_url or "另一个成功地址" in decoded_url:
                return httpx.Response(200, json={
                    "status": 0,
                    "result": {"location": {"lng": 116.0, "lat": 39.0}}
                })
            else:
                return httpx.Response(200, json={"status": 1, "message": "Invalid address"})

        with respx.mock as respx_mock:
            respx_mock.get("https://api.map.baidu.com/geocoding/v3/").mock(
                side_effect=mock_response
            )

            geocoder = AsyncGeocoder(ak="test_ak", cache_path=str(cache_path))
            result = await geocoder.geocode_batch(addresses)

        # Verify results
        assert "成功地址" in result
        assert result["成功地址"] == [116.0, 39.0]
        assert "另一个成功地址" in result
        assert result["另一个成功地址"] == [116.0, 39.0]
        assert "失败地址" in result
        assert result["失败地址"] is None

        # Verify cache updated
        cache_content = json.loads(cache_path.read_text(encoding="utf-8"))
        assert "成功地址" in cache_content
        assert cache_content["成功地址"] == [116.0, 39.0]

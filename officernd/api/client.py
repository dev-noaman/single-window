"""
HTTP client for OfficeRnD API with authentication handling.
"""

import logging
import time
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api.config import AppConfig, OAuthConfig
from api.models import ApiResponse, HttpMethod


logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class ApiClientError(Exception):
    """Raised when API calls fail."""
    pass


class OAuthClient:
    """Handles OAuth token retrieval with automatic refresh on expiry."""

    # Refresh token 60 seconds before actual expiry
    EXPIRY_BUFFER_SECONDS = 60

    def __init__(self, config: OAuthConfig, timeout: int = 25):
        self._config = config
        self._timeout = timeout
        self._token: Optional[str] = None
        self._expires_at: Optional[float] = None  # Unix timestamp

    def get_token(self) -> str:
        """Get or refresh access token."""
        if self._token and self._is_token_valid():
            return self._token

        self._token = self._fetch_token()
        return self._token

    def _is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        if self._expires_at is None:
            return False
        # Check if token expires within buffer period
        return time.time() < (self._expires_at - self.EXPIRY_BUFFER_SECONDS)

    def _fetch_token(self) -> str:
        """Fetch a new access token from OAuth server."""
        payload = self._build_token_payload()
        
        logger.info(f"Requesting OAuth token with grant_type={self._config.grant_type}")
        
        try:
            response = requests.post(
                self._config.token_url,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self._timeout
            )
            response.raise_for_status()
            
        except requests.RequestException as e:
            # Try to get response body for debugging
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = f"{e} - Response: {e.response.text}"
                except:
                    pass
            logger.error(f"Token request failed: {error_detail}")
            raise AuthenticationError(f"Failed to obtain access token: {error_detail}") from e

        data = response.json()
        token = data.get("access_token")
        
        if not token:
            raise AuthenticationError(f"No access_token in response: {data}")

        # Track token expiry from expires_in field
        expires_in = data.get("expires_in")
        if expires_in:
            self._expires_at = time.time() + int(expires_in)
            logger.info(f"Successfully obtained access token, expires in {expires_in}s")
        else:
            # Default to 1 hour if expires_in not provided
            self._expires_at = time.time() + 3600
            logger.warning("No expires_in in token response, defaulting to 1 hour")

        return token

    def _build_token_payload(self) -> Dict[str, str]:
        """Build token request payload based on grant type."""
        base_payload = {
            "client_id": self._config.client_id,
            "client_secret": self._config.client_secret,
        }

        if self._config.grant_type == "password":
            payload = {
                **base_payload,
                "grant_type": "password",
                "username": self._config.username,
                "password": self._config.password,
            }
            if self._config.scope:
                payload["scope"] = self._config.scope
            if self._config.audience:
                payload["audience"] = self._config.audience
            return payload
        
        elif self._config.grant_type == "client_credentials":
            payload = {
                **base_payload,
                "grant_type": "client_credentials",
            }
            if self._config.scope:
                payload["scope"] = self._config.scope
            if self._config.audience:
                payload["audience"] = self._config.audience
            return payload
        
        else:
            raise AuthenticationError(f"Unsupported grant type: {self._config.grant_type}")

    def clear_token(self) -> None:
        """Clear cached token (for re-authentication)."""
        self._token = None
        self._expires_at = None


class OfficeRnDClient:
    """HTTP client for OfficeRnD API with automatic token refresh on 401."""

    def __init__(self, config: AppConfig):
        self._config = config
        self._oauth = OAuthClient(config.oauth, config.api.timeout_seconds)
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        token = self._oauth.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def build_url(self, resource: str) -> str:
        """Build full API URL for a resource."""
        return f"{self._config.api.api_base}/{resource}"

    def request(
        self,
        method: HttpMethod,
        url: str,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        """Make an authenticated API request with automatic retry on 401."""
        headers = self._get_headers()
        timeout = self._config.api.timeout_seconds

        logger.debug(f"{method.name} {url}")

        try:
            if method == HttpMethod.GET:
                response = self._session.get(url, headers=headers, timeout=timeout)
            elif method == HttpMethod.POST:
                response = self._session.post(url, headers=headers, json=json_body, timeout=timeout)
            elif method == HttpMethod.PUT:
                response = self._session.put(url, headers=headers, json=json_body, timeout=timeout)
            elif method == HttpMethod.DELETE:
                response = self._session.delete(url, headers=headers, timeout=timeout)
            else:
                return ApiResponse(
                    status_code=0,
                    payload=None,
                    error=f"Unsupported method: {method}",
                    url=url,
                    method=method.name,
                )

            # Handle 401 Unauthorized - refresh token and retry once
            if response.status_code == 401:
                logger.warning("Received 401 response, refreshing token and retrying...")
                self._oauth.clear_token()
                headers = self._get_headers()  # Get fresh token
                
                # Retry the request once with fresh token
                if method == HttpMethod.GET:
                    response = self._session.get(url, headers=headers, timeout=timeout)
                elif method == HttpMethod.POST:
                    response = self._session.post(url, headers=headers, json=json_body, timeout=timeout)
                elif method == HttpMethod.PUT:
                    response = self._session.put(url, headers=headers, json=json_body, timeout=timeout)
                elif method == HttpMethod.DELETE:
                    response = self._session.delete(url, headers=headers, timeout=timeout)

            try:
                payload = response.json()
            except ValueError:
                payload = response.text 

            error = None
            if response.status_code >= 400:
                error = str(payload)[:900] if payload else f"HTTP {response.status_code}"

            return ApiResponse(
                status_code=response.status_code,
                payload=payload,
                error=error,
                url=url,
                method=method.name,
            )

        except requests.Timeout:
            logger.warning(f"Request timed out: {url}")
            return ApiResponse(
                status_code=0,
                payload=None,
                error="Request timed out",
                url=url,
                method=method.name,
            )
        except requests.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            return ApiResponse(
                status_code=0,
                payload=None,
                error=str(e),
                url=url,
                method=method.name,
            )

    def get(self, resource: str, query_params: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """GET request to a resource.
        
        Args:
            resource: The API resource path
            query_params: Optional query parameters to append to URL
            
        Returns:
            ApiResponse object with response data
        """
        url = self.build_url(resource)
        if query_params:
            from urllib.parse import urlencode
            url = f"{url}?{urlencode(query_params)}"
        return self.request(HttpMethod.GET, url)

    def get_one(self, resource: str, resource_id: str) -> ApiResponse:
        """GET request for a single resource by ID."""
        url = f"{self.build_url(resource)}/{resource_id}"
        return self.request(HttpMethod.GET, url)

    def post(self, resource: str, data: Dict[str, Any]) -> ApiResponse:
        """POST request to a resource."""
        url = self.build_url(resource)
        return self.request(HttpMethod.POST, url, json_body=data)

    def close(self) -> None:
        """Close session."""
        self._session.close()

    def __enter__(self) -> "OfficeRnDClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

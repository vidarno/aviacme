"""Functions that interacts with the loadbalancer"""
import logging

import attr
import json
from avi.sdk.avi_api import ApiSession

logger = logging.getLogger(__name__)

# suds is very noisy
#logging.getLogger("suds.client").setLevel(logging.CRITICAL)
from requests.packages import urllib3
urllib3.disable_warnings()

class LoadBalancerError(Exception):
    """Superclass for all load balancer exceptions."""


class CouldNotConnectToBalancerError(LoadBalancerError):
    """Raised when a connection to the load balancer could not be made"""


class TenantNotFoundError(LoadBalancerError):
    """Raised when the tenant was not found"""


class CSRNotFoundError(LoadBalancerError):
    """Raised when the CSR was not found on the device"""


class AccessDeniedError(LoadBalancerError):
    """Raised when the device denies access"""


class NotFoundError(LoadBalancerError):
    """Raised when the specified resource was not found on the load balancer"""


@attr.s
class LoadBalancer:
    """Represent the LoadBalancer"""

    avi = attr.ib()
    tenant = attr.ib()

    @classmethod
    def create_from_config(cls, config):
        """Connects to AVI"""
        tenant = config.tenant

        avi = ApiSession.get_session(config.avi, config.lb_user, config.lb_pwd, tenant = config.tenant)
        return cls(avi, config.tenant)

    def get_csr(self, tenant, csrname: str) -> str:
        """Downloads the specified csr"""
        try:
            query = 'name=%s' % csrname
            result = self.avi.get_object_by_name('sslkeyandcertificate', csrname, tenant=tenant)
        except Exception as e:
            raise NotFoundError
        return result['certificate']['certificate_signing_request']

    def upload_certificate(self, tenant, name: str, certificates: str) -> None:
        """Uploads a new certificate to AVI"""
        try:
            query = 'name=%s' % name
            result_obj = self.avi.get_object_by_name('sslkeyandcertificate', name, tenant=tenant)
        except Exception as e:
            raise NotFoundError
        result_obj['certificate']['certificate']=certificates
        put_result = self.avi.put('sslkeyandcertificate/%s' % result_obj['uuid'], data=result_obj)

    @staticmethod
    def _handle_error_from_load_balancer(error):
        logger.debug("Received error from the load balancer: %s", error)
        if "folder not found" in error.fault.faultstring:
            raise TenantNotFoundError() from error
        elif "Not Found" in error.fault.faultstring:
            raise NotFoundError() from error
        elif "Access Denied:" in error.fault.faultstring:
            raise AccessDeniedError() from error
        else:
            raise

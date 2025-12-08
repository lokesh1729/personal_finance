"""
Custom exceptions for python_scripts package.
"""


class MutualFundSearchIdNotFoundError(Exception):
    """Raised when a mutual fund search_id cannot be found from Groww API."""
    
    def __init__(self, mf_name: str, message: str = None):
        self.mf_name = mf_name
        self.message = message or f"Could not find search_id for mutual fund: {mf_name}"
        super().__init__(self.message)


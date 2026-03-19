class AmshaException(Exception):
    """Base exception for all Amsha errors"""
    pass

class AmshaConfigurationException(AmshaException):
    """Specific strict configuration validation error"""
    def __init__(self, message: str, errors: list[str] = None):
        super().__init__(message)
        self.errors = errors or []
        
    def __str__(self):
        base_msg = super().__str__()
        if self.errors:
            error_details = "\n".join(f" - {err}" for err in self.errors)
            return f"{base_msg}\nValidation Errors:\n{error_details}"
        return base_msg

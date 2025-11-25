"""
Test file to validate AI audit chunking functionality

This file contains intentional violations to test chunked review.
"""

from typing import Optional

class TestService:
    """Test service with violations"""
    
    def __init__(self):
        # Violation: Manual instantiation
        self.data = {}
    
    def process(self, value):  # Missing type hints
        """Process value"""
        return str(value)


class AnotherService:
    """Another test service"""
    
    def handle(self, item: str) -> Optional[str]:
        """Good method with types"""
        if not item:
            return None
        return item.upper()

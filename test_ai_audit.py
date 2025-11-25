"""
Test file to validate AI audit functionality

This file contains intentional architectural violations to test the AI audit.
"""

from typing import Optional

class TestService:
    """Test service with some violations"""
    
    def __init__(self):
        # ❌ BAD: Manual instantiation (should be injected)
        from nikhil.amsha.toolkit.crew_forge.repo.adapters.mongo.mongo_agent_repository import MongoAgentRepository
        self.repo = MongoAgentRepository()  # Violation: Direct instantiation
    
    def get_agent(self, agent_id):  # ❌ Missing type hints
        """Get agent by ID"""
        try:
            return self.repo.get_agent_by_id(agent_id)
        except:
            raise Exception("Failed to get agent")  # ❌ Generic exception
    
    def process_data(self, data: dict) -> Optional[str]:
        """Process some data - this is good"""
        if not data:
            return None
        return str(data)

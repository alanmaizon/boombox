import os
import importlib
from agents.coordinator_agent import CoordinatorAgent
import agents

def test_api_key_mapping(monkeypatch):
    """Ensure API_KEY is correctly mapped to GEMINI_API_KEY for the agents."""
    monkeypatch.setenv("API_KEY", "test-secret-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    importlib.reload(agents)
    
    assert os.environ.get("GEMINI_API_KEY") == "test-secret-key"

def test_coordinator_agent_initialization():
    """Test that the CoordinatorAgent initializes with all sub-agents correctly."""
    agent = CoordinatorAgent()
    assert agent.name == "CoordinatorAgent"
    assert len(agent.sub_agents) == 6

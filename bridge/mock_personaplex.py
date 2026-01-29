# File: bridge/mock_personaplex.py

class MockPersonaPlex:
    """
    Simulates the injection point of the PersonaPlex model.
    """
    def format_injection(self, context_text: str):
        # This simulates the steering tag that will be injected 
        # into the PersonaPlex input buffer
        return f"<context>{context_text}</context>"
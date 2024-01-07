

class World:
    """
    Class for managing the world state. There should only ever be one instance
    - Enforce singleton?
    - Own WorldClock()? Would make sense if singleton enforced
    """
    def __init__(self):
        pass

    def initialize(self) -> bool:
        return True

    def update(self):
        # Update internal logic
        pass

    def render(self):
        # Render GUI
        pass
import os

class Settings:
    PROJECT_NAME: str = "INDUSTRIALGUARD AI"
    TAGLINE: str = "Detect. Understand. Prioritize. Act."
    VERSION: str = "1.0.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    SIMULATION_INTERVAL_SEC: float = float(os.getenv("SIMULATION_INTERVAL_SEC", 1.0))
    HISTORY_MAX_LEN: int = int(os.getenv("HISTORY_MAX_LEN", 100))
    ISOLATION_FOREST_CONTAMINATION: float = float(os.getenv("ISOLATION_FOREST_CONTAMINATION", 0.05))

settings = Settings()

from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate_jml(self, java_code: str, feedback: str = "") -> str:
        pass
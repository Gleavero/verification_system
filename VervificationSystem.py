from JMLGenerator import JMLGenerator
from KeYVerifier import KeYVerifier
from llm_interface import LLMInterface
from ollama_client import OllamaClient
from SpotBugsAnalyzer import SpotBugsAnalyzer


class VerificationSystem:
    def __init__(self, llm: LLMInterface, max_retries: int = 7):
        self.generator = JMLGenerator(llm)
        self.spotbugs = SpotBugsAnalyzer()
        self.key = KeYVerifier()
        self.max_retries = max_retries

    def run(self, initial_code: str):
        current_code = initial_code
        feedback = ""
        for attempt in range(self.max_retries):
            try:
                annotated_code = self.generator.generate_and_validate(current_code, feedback)
            except ValueError as e:
                feedback = f"JML compilation failed: {str(e)}"
                print(feedback)
                continue

            # Проверка SpotBugs:
            spotbugs_errors = self.spotbugs.run("Temp.java")
            # Проверка KeY
#            key_result = self.key.verify("Temp.java")

            if not spotbugs_errors: # and key_result["success"]:
                print("Verification successful!")
                return

            # Формирование обратной связи
            feedback = "Issues found:\n"
            if spotbugs_errors:
                feedback += "- SpotBugs errors:\n" + "\n".join(spotbugs_errors) + "\n"
            if not key_result["success"]:
                feedback += "- KeY errors:\n" + "\n".join(key_result["errors"]) + "\n"

            current_code = annotated_code

        print("Verification failed after max retries.")

# Пример использования
if __name__ == "__main__":
    llm = OllamaClient(model="qwen2.5-coder:1.5b")
    system = VerificationSystem(llm)
    java_code = """
    public class Calculator {
        public int add(int a, int b) {
            return a + b;
        }
    }
    """
    system.run(java_code)

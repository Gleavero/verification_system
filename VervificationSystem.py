from JMLGenerator import JMLGenerator
from KeYVerifier import KeYVerifier
from llm_interface import LLMInterface
from ollama_client import OllamaClient
from SpotBugsAnalyzer import SpotBugsAnalyzer
import os
import tempfile

class VerificationSystem:
    def __init__(self, llm: LLMInterface, max_retries: int = 7):
        self.generator = JMLGenerator(llm)
        self.spotbugs = SpotBugsAnalyzer()
        self.key = KeYVerifier()
        self.max_retries = max_retries

    def run(self, initial_code: str):
        current_code = initial_code
        feedback = ""
        
        # Extract class name for file naming
        class_name = self.generator._get_code_class_name(initial_code) or "Temp"
        java_file_path = f"{class_name}.java"
        
        for attempt in range(self.max_retries):
            print(f"Attempt {attempt+1}/{self.max_retries}")
            
            try:
                # Generate and validate annotations
                annotated_code = self.generator.generate_and_validate(current_code, feedback)
                
                # Write to file for analysis
                with open(java_file_path, "w") as f:
                    f.write(annotated_code)
                
                # Run SpotBugs
                spotbugs_errors = self.spotbugs.run(java_file_path)
                
                # Run KeY verification
                key_result = self.key.verify(java_file_path)
                
                # Check if successful
                if not spotbugs_errors and key_result["success"]:
                    print("✅ Verification successful!")
                    return annotated_code
                
                # Generate feedback for next attempt
                feedback = "Issues found:\n"
                if spotbugs_errors:
                    feedback += "- SpotBugs errors:\n" + "\n".join(spotbugs_errors) + "\n"
                if not key_result["success"]:
                    feedback += "- KeY errors:\n" + "\n".join(key_result["errors"]) + "\n"
                
                print(feedback)
                current_code = annotated_code
                
            except ValueError as e:
                feedback = f"JML compilation failed: {str(e)}"
                print(feedback)
            
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                
        print("❌ Verification failed after max retries.")
        return current_code  # Return the last attempt

# Example usage
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

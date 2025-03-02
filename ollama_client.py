import requests
from llm_interface import LLMInterface

class OllamaClient(LLMInterface):
    def __init__(self, 
                 model: str = "codellama:7b", 
                 base_url: str = "http://localhost:11434",
                 temperature: float = 0.7):
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

    def generate_jml(self, java_code: str, feedback: str = "") -> str:
        """Generate JML annotations for the given Java code."""
        prompt = self._build_prompt(java_code, feedback)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": self.temperature}
                },
                timeout=60  # Add timeout to prevent hanging
            )
            response.raise_for_status()
            annotated_code = response.json().get("response", "")
            
            # Extract just the Java code if the model wrapped it in markdown
            if "```java" in annotated_code and "```" in annotated_code:
                start = annotated_code.find("```java") + 7
                end = annotated_code.rfind("```")
                annotated_code = annotated_code[start:end].strip()
                
            return annotated_code
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ollama connection failed: {str(e)}")

    def _build_prompt(self, java_code: str, feedback: str = "") -> str:
        """Build the prompt for the LLM to generate JML annotations."""
        # Example of well-annotated code
        sample_code = """
// It establishes that the sum is always non-negative and within the range of Integer

public class Calculator {

    /*@
         requires a != null && b != null;
         ensures \\result >= 0;
         ensures \\result <= Integer.MAX_VALUE; // assuming Integer.MAX_VALUE is used for calculation
     @*/
    public int add(int a, int b) {
        return a + b;
    }
}
"""

        # Create the prompt with feedback if provided
        prompt = f"""
        You are a Java Modeling Language (JML) expert. Generate correct JML annotations 
        for the following Java code following these rules:
        
        1. Use requires/ensures clauses for method contracts
        2. Define class invariants where needed
        3. Handle nullability and exceptions properly
        4. Use JML keywords correctly (e.g., signals, assignable)
        5. Validate data ranges with invariant clauses
        6. Do not use comments inside annotations
        
        Return ONLY the Java code with JML annotations in Java comment format without explanations.
        Return ONLY result code without any Markdown syntax.
        
        Example of code with JML annotations:
        {sample_code}
        """
        
        # Add feedback if available
        if feedback:
            prompt += f"""
        Previous attempt had these issues:
        {feedback}
        
        Please address these issues in your new annotations.
        """
            
        # Add the code to annotate
        prompt += f"""
        Java Code to annotate:
        {java_code}
        """
        
        return prompt

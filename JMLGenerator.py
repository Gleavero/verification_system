import subprocess
import re

import llm_interface

class JMLGenerator:
    def __init__(self, llm: llm_interface):
        self.llm = llm

    def _compile_with_openjml(self, file_path: str) -> bool:
        result = subprocess.run(
            ["openjml", file_path],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return "error" not in result.stdout

    def generate_and_validate(self, java_code: str, feedback: str = "") -> str:
        annotated_code = self.llm.generate_jml(java_code, feedback)
        className = self._get_code_class_name(annotated_code)
        fileName = className+".java"
        with open(fileName, "w") as f:
            f.write(annotated_code)
        if self._compile_with_openjml(fileName):
            return annotated_code
        else:
            raise ValueError("JML validation failed")

    def _get_code_class_name(self, code: str):
        # Regex pattern to match Java class definitions
        pattern = r'\b(?:public|private|protected)?\s+class\s+(\w+)'

        # Search for the pattern in the Java code
        match = re.search(pattern, code)
        print(f"Found class Name : %s", match.group(1))

        # If a match is found, return the class name (group 1)
        if match:
            return match.group(1)
        else:
            return None

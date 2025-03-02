import subprocess
import re
import os
import tempfile
from pathlib import Path

class JMLGenerator:
    def __init__(self, llm):
        self.llm = llm

    def _compile_with_openjml(self, file_path: str) -> dict:
        """Run OpenJML on the Java file and return compilation result with details."""
        result = subprocess.run(
            ["openjml", file_path],
            capture_output=True,
            text=True
        )
        success = "error" not in result.stdout.lower()
        return {
            "success": success,
            "output": result.stdout,
            "errors": [line for line in result.stdout.split('\n') if "error" in line.lower()]
        }

    def generate_and_validate(self, java_code: str, feedback: str = "") -> str:
        """Generate JML annotations and validate them with OpenJML."""
        # Generate annotated code
        annotated_code = self.llm.generate_jml(java_code, feedback)
        
        # Extract class name
        class_name = self._get_code_class_name(annotated_code)
        if not class_name:
            raise ValueError("Could not extract class name from the Java code")
        
        # Create a temporary directory for the file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Java file with the correct name matching the class
            java_file_path = os.path.join(temp_dir, f"{class_name}.java")
            
            with open(java_file_path, "w") as f:
                f.write(annotated_code)
            
            # Compile with OpenJML
            result = self._compile_with_openjml(java_file_path)
            
            if result["success"]:
                # Also save a permanent copy
                try:
                    output_dir = Path("output")
                    output_dir.mkdir(exist_ok=True)
                    with open(output_dir / f"{class_name}.java", "w") as f:
                        f.write(annotated_code)
                except Exception as e:
                    print(f"Warning: Failed to save permanent copy: {e}")
                
                return annotated_code
            else:
                error_msg = "\n".join(result["errors"]) if result["errors"] else "Unknown compilation error"
                raise ValueError(f"JML validation failed: {error_msg}")

    def _get_code_class_name(self, code: str):
        """Extract the class name from Java code."""
        # First try to find public class
        pattern = r'\b(?:public|private|protected)?\s+class\s+(\w+)'
        match = re.search(pattern, code)
        
        if match:
            return match.group(1)
        
        # Try finding any class if there's no public class
        pattern = r'class\s+(\w+)'
        match = re.search(pattern, code)
        
        if match:
            return match.group(1)
            
        return None

import subprocess
import os
import tempfile

class KeYVerifier:
    def verify(self, file_path: str) -> dict:
        """
        Verify Java file with JML annotations using KeY prover.
        
        Args:
            file_path: Path to the Java file
        
        Returns:
            Dictionary with verification results
        """
        # Make sure the file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "errors": [f"File not found: {file_path}"]
            }
        
        try:
            result = subprocess.run(
                ["key", "--prove", file_path],
                capture_output=True,
                text=True,
                timeout=60  # Add timeout to prevent indefinite hanging
            )
            
            return {
                "success": "Proof completed" in result.stdout,
                "errors": self._parse_key_errors(result.stdout)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "errors": ["KeY verification timed out"]
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"KeY verification error: {str(e)}"]
            }

    def _parse_key_errors(self, output: str) -> list:
        """Extract error messages from KeY output."""
        errors = []
        
        for line in output.split("\n"):
            if "ERROR" in line or "error" in line.lower():
                errors.append(line.strip())
                
        return errors

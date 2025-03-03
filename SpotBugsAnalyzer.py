import subprocess
import os
import tempfile
import re

class SpotBugsAnalyzer:
    def run(self, file_path: str) -> list:
        """
        Run SpotBugs on a Java file.
        
        Args:
            file_path: Path to Java file
            
        Returns:
            List of found errors
        """
        # Make sure the file exists
        if not os.path.exists(file_path):
            return [f"File not found: {file_path}"]
        
        # Need to compile the Java file first
        try:
            compile_result = subprocess.run(
                ["javac", file_path],
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return [f"Compilation failed: {compile_result.stderr}"]
            
            # Get the class file path (same as java file but with .class extension)
            class_file = os.path.splitext(file_path)[0] + ".class"
            if not os.path.exists(class_file):
                return ["Compilation completed but class file not found"]
            
            # Run SpotBugs on the class file
            result = subprocess.run(
                ["spotbugs", "-textui", class_file],
                capture_output=True,
                text=True
            )
            
            print(f"Output of SpotBugs - \n {result.stdout}")
            
            return self._parse_errors(result.stdout + result.stderr)
            
        except Exception as e:
            return [f"Error running SpotBugs: {str(e)}"]

    def _parse_errors(self, output: str) -> list:
        """Parse errors from SpotBugs output."""
        errors = []
        
        # Look for specific SpotBugs error patterns
        bug_pattern = r'M\s+([A-Z_]+):\s+(.*)'
        
        for line in output.split("\n"):
            if "ERROR" in line or "error" in line.lower():
                errors.append(line.strip())
            
            # Look for bug patterns
            match = re.search(bug_pattern, line)
            if match:
                bug_type = match.group(1)
                description = match.group(2)
                errors.append(f"SpotBugs found issue: {bug_type} - {description}")
                
        return errors

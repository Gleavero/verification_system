import subprocess


class SpotBugsAnalyzer:
    def run(self, file_path: str) -> list:
        result = subprocess.run(
            ["spotbugs", "-textui", file_path],
            capture_output=True,
            text=True
        )
        return self._parse_errors(result.stdout)

    def _parse_errors(self, output: str) -> list:
        errors = []
        for line in output.split("\n"):
            if "ERROR" in line:
                errors.append(line.strip())
        return errors
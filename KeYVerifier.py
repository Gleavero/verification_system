import subprocess


class KeYVerifier:
    def verify(self, file_path: str) -> dict:
        result = subprocess.run(
            ["key", "--prove", file_path],
            capture_output=True,
            text=True
        )
        return {
            "success": "Proof completed" in result.stdout,
            "errors": self._parse_key_errors(result.stdout)
        }

    def _parse_key_errors(self, output: str) -> list:
        return [line for line in output.split("\n") if "ERROR" in line]
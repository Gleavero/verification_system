# JML Annotation Research

This project evaluates the capabilities of different Language Models (LLMs) in generating Java Modeling Language (JML) annotations for Java code.

## Overview

The system uses various LLMs to generate JML annotations for Java code, then validates these annotations using:

1. OpenJML - For compilation and syntax checking
2. SpotBugs - For static analysis
3. KeY - For formal verification

## Requirements

- Python 3.8+
- Java JDK 11+
- OpenJML
- SpotBugs
- KeY Verification tool
- Ollama (for running local LLMs)

## Installation

1. Clone this repository
2. Install the required Python packages:

   ```bash
   pip install matplotlib pandas seaborn tqdm requests
   ```

3. Install Java dependencies:

   ```
   # Install OpenJML
   # See https://www.openjml.org/downloads/

   # Install SpotBugs
   # See https://spotbugs.github.io/

   # Install KeY
   # See https://www.key-project.org/download/
   ```

4. Install and configure Ollama:

   ```bash
   # See https://ollama.ai/

   # Download required models
   ollama pull codellama:7b
   ollama pull qwen2.5-coder:1.5b
   ```

## Project Structure

```
.
├── JMLEvaluation.py         # Main evaluation system
├── JMLEvaluatorRunner.py    # Command-line runner
├── JMLGenerator.py          # JML annotation generator
├── KeYVerifier.py           # Formal verification interface
├── SpotBugsAnalyzer.py      # Static analysis interface
├── VerificationSystem.py    # Integrated verification system
├── llm_interface.py         # Abstract LLM interface
├── ollama_client.py         # Ollama API client
├── test_cases/              # Java test cases
│   └── Calculator.java      # Sample test case
└── results/                 # Results directory
    ├── code/                # Generated JML-annotated code
    ├── data/                # JSON and CSV data
    └── graphs/              # Performance visualizations
```

## Usage

Run the evaluation with default settings:

```bash
python JMLEvaluatorRunner.py
```

Specify models and other parameters:

```bash
python JMLEvaluatorRunner.py --models codellama:7b qwen2.5-coder:1.5b --test-cases ./my_test_cases --results ./my_results --max-retries 5
```

## Adding Test Cases

Add Java files to the `test_cases` directory. The system will automatically discover and process them.

## Visualization

The system generates several visualizations:

1. Success rates by model and verification method
2. Average retries by model
3. Average execution time by model
4. Radar chart of success metrics (if multiple models)
5. Success by test case and model (if multiple test cases)
6. Success rate heatmap (if multiple models and test cases)

## Sample JML Annotations

The project includes sample JML annotations for reference:

```java
// It establishes that the sum is always non-negative and within the range of Integer

public class Calculator {

    /*@
         requires a != null && b != null;
         ensures \result >= 0;
         ensures \result <= Integer.MAX_VALUE; // assuming Integer.MAX_VALUE is used for calculation
     @*/
    public int add(int a, int b) {
        return a + b;
    }
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

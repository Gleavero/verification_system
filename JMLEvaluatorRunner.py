#!/usr/bin/env python3
"""
Main runner for JML annotation research project.
Evaluates different LLM models on their ability to generate JML annotations.
"""

import argparse
import logging
from JMLEvaluation import JMLResearchEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("jml_research.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("JMLResearch")

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate LLM capabilities for generating JML annotations"
    )
    
    parser.add_argument("--models", type=str, nargs="+", default=["qwen2.5-coder:1.5b","codellama:7b"])
    parser.add_argument("--test-cases", type=str,default="./test_cases")
    parser.add_argument("--results", type=str,default="./results")
    
    args = parser.parse_args()

    evaluator = JMLEvaluation(
        models: args.models,
        test_cases_dir: args.test-cases,
        output_dir: args.results
    )

    evaluator.run_evaluation()



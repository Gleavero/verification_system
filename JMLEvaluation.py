"""
Main runner for JML annotation evaluation research.
Coordinates the evaluation of different LLM models for JML annotation generation.
"""

import os
import json
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

from llm_interface import LLMInterface
from ollama_client import OllamaClient
from JMLGenerator import JMLGenerator
from SpotBugsAnalyzer import SpotBugsAnalyzer
from KeYVerifier import KeYVerifier


class JMLResearchEvaluator:
    """
    Coordinates the evaluation of different LLM models for JML annotation generation.
    """

    def __init__(self, 
                 models: List[Dict[str, Any]],
                 test_cases_dir: str = "test_cases",
                 output_dir: str = "results",
                 max_retries: int = 3):
        """
        Initialize the JML research evaluator.

        Args:
            models: List of model configurations with name, client type, and parameters
            test_cases_dir: Directory containing Java test cases
            output_dir: Directory to store results
            max_retries: Maximum number of retries for generation
        """
        self.models = models
        self.test_cases_dir = test_cases_dir
        self.output_dir = output_dir
        self.max_retries = max_retries

        # Ensure directories exist
        os.makedirs(test_cases_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "code"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "data"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "graphs"), exist_ok=True)

        # Results storage
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "models": [model["name"] for model in models],
            "test_cases": [],
            "metrics": {}
        }

    def load_test_cases(self) -> List[Dict[str, str]]:
        """
        Load all Java test cases from the test cases directory.

        Returns:
            List of test case objects with name and code
        """
        test_cases = []

        for file_path in Path(self.test_cases_dir).glob("*.java"):
            with open(file_path, "r") as f:
                test_cases.append({
                    "name": file_path.stem,
                    "code": f.read()
                })

        if not test_cases:
            # Add a sample test case if none exist
            sample_case = {
                "name": "Calculator",
                "code": """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public double divide(int a, int b) {
        return (double) a / b;
    }
}
                """
            }
            test_cases.append(sample_case)

            # Save the sample test case
            with open(os.path.join(self.test_cases_dir, f"{sample_case['name']}.java"), "w") as f:
                f.write(sample_case["code"])

        return test_cases

    def run_evaluation(self):
        """
        Run the full evaluation process for all models and test cases.
        """
        test_cases = self.load_test_cases()
        self.results["test_cases"] = [case["name"] for case in test_cases]

        print(f"🔍 Evaluating {len(self.models)} models on {len(test_cases)} test cases")

        # Set up tracking metrics for each model
        for model in self.models:
            model_name = model["name"]
            self.results["metrics"][model_name] = {
                "success_rate": 0,
                "avg_retries": 0,
                "compile_success": 0,
                "spotbugs_success": 0,
                "key_success": 0,
                "execution_time": 0,
                "test_results": {}
            }

        # Evaluate each test case with each model
        for test_case in tqdm(test_cases, desc="Processing test cases"):
            for model_config in self.models:
                model_name = model_config["name"]
                print(f"\n📊 Testing {model_name} on {test_case['name']}")

                try:
                    # Initialize LLM client based on model config
                    llm = self._create_llm_client(model_config)

                    # Create verification system
                    spotbugs = SpotBugsAnalyzer()
                    key_verifier = KeYVerifier()
                    jml_generator = JMLGenerator(llm)

                    # Measure execution time
                    start_time = time.time()

                    # Run the evaluation
                    test_result = self._evaluate_single_case(
                        test_case["code"], 
                        test_case["name"],
                        jml_generator, 
                        spotbugs, 
                        key_verifier
                    )

                    # Record execution time
                    execution_time = time.time() - start_time
                    test_result["execution_time"] = execution_time

                    # Store the results
                    self.results["metrics"][model_name]["test_results"][test_case["name"]] = test_result

                    # Update aggregate metrics
                    self._update_metrics(model_name, test_result)

                except Exception as e:
                    print(f"❌ Error evaluating {model_name} on {test_case['name']}: {str(e)}")
                    self.results["metrics"][model_name]["test_results"][test_case["name"]] = {
                        "error": str(e),
                        "success": False
                    }

        # Finalize the aggregate metrics
        self._finalize_metrics()

        # Save results
        self._save_results()

        # Generate graphs
        self._generate_graphs()

        print("\n✅ Evaluation complete! Results saved to", self.output_dir)

    def _create_llm_client(self, model_config: Dict[str, Any]) -> LLMInterface:
        """
        Create an LLM client based on model configuration.

        Args:
            model_config: Configuration for the model

        Returns:
            An initialized LLM client
        """
        client_type = model_config.get("client_type", "ollama")

        if client_type == "ollama":
            return OllamaClient(
                model=model_config["model_name"],
                base_url=model_config.get("base_url", "http://localhost:11434"),
                temperature=model_config.get("temperature", 0.7)
            )
        else:
            raise ValueError(f"Unsupported client type: {client_type}")

    def _evaluate_single_case(self, 
                              java_code: str, 
                              case_name: str,
                              jml_generator: JMLGenerator, 
                              spotbugs: SpotBugsAnalyzer, 
                              key_verifier: KeYVerifier) -> Dict[str, Any]:
        """
        Evaluate a single test case with a specific model.

        Args:
            java_code: Java code to annotate
            case_name: Name of the test case
            jml_generator: JML generator instance
            spotbugs: SpotBugs analyzer instance
            key_verifier: KeY verifier instance

        Returns:
            Dictionary with evaluation results
        """
        result = {
            "success": False,
            "compile_success": False,
            "spotbugs_success": False,
            "key_success": False,
            "retries": 0,
            "annotations": None,
            "errors": [],
            "class_name": None
        }

        current_code = java_code
        feedback = ""

        # Extract initial class name for reference
        try:
            result["class_name"] = jml_generator._get_code_class_name(java_code)
        except Exception:
            result["class_name"] = case_name

        # Attempt to generate and validate JML annotations
        for attempt in range(self.max_retries):
            result["retries"] = attempt + 1

            try:
                annotated_code = jml_generator.generate_and_validate(current_code, feedback)
                result["compile_success"] = True
                result["annotations"] = annotated_code

                # Save the annotated code
                code_file_path = os.path.join(
                    self.output_dir, 
                    "code", 
                    f"{case_name}_{result['class_name']}.java"
                )
                with open(code_file_path, "w") as f:
                    f.write(annotated_code)

                # Check with SpotBugs
                file_path = f"{result['class_name']}.java"
                spotbugs_errors = spotbugs.run(file_path)
                if not spotbugs_errors:
                    result["spotbugs_success"] = True
                else:
                    result["errors"].append({"type": "spotbugs", "messages": spotbugs_errors})

                # Check with KeY verifier
                try:
                    key_result = key_verifier.verify(file_path)
                    if key_result["success"]:
                        result["key_success"] = True
                    else:
                        result["errors"].append({"type": "key", "messages": key_result["errors"]})
                except Exception as e:
                    print(f"Warning: KeY verification failed with error: {str(e)}")
                    result["errors"].append({"type": "key", "messages": [str(e)]})

                # Overall success
                result["success"] = (
                    result["compile_success"] and 
                    result["spotbugs_success"] and 
                    result["key_success"]
                )

                # If successful or this is the last attempt, break
                if result["success"] or attempt == self.max_retries - 1:
                    break

                # Build feedback for next attempt
                feedback = "Issues found:\n"
                if spotbugs_errors:
                    feedback += "- SpotBugs errors:\n" + "\n".join(spotbugs_errors) + "\n"
                if not result["key_success"]:
                    key_errors = result["errors"][-1]["messages"] if result["errors"] else []
                    feedback += "- KeY errors:\n" + "\n".join(key_errors) + "\n"

                current_code = annotated_code

            except ValueError as e:
                feedback = f"JML compilation failed: {str(e)}"
                result["errors"].append({"type": "compilation", "messages": [str(e)]})

                if attempt == self.max_retries - 1:
                    # Last attempt failed
                    result["success"] = False
                    break

        return result

    def _update_metrics(self, model_name: str, test_result: Dict[str, Any]):
        """
        Update the aggregate metrics for a model with a new test result.

        Args:
            model_name: Name of the model
            test_result: Results from a single test case evaluation
        """
        metrics = self.results["metrics"][model_name]

        # Increment counters
        if test_result.get("success", False):
            metrics["success_rate"] += 1
        if test_result.get("compile_success", False):
            metrics["compile_success"] += 1
        if test_result.get("spotbugs_success", False):
            metrics["spotbugs_success"] += 1
        if test_result.get("key_success", False):
            metrics["key_success"] += 1

        # Track retries and execution time
        metrics["avg_retries"] += test_result.get("retries", 0)
        metrics["execution_time"] += test_result.get("execution_time", 0)

    def _finalize_metrics(self):
        """
        Finalize the aggregate metrics by computing averages.
        """
        test_count = len(self.results["test_cases"])
        if test_count == 0:
            return

        for model_name, metrics in self.results["metrics"].items():
            # Convert counters to percentages
            metrics["success_rate"] = (metrics["success_rate"] / test_count) * 100
            metrics["compile_success"] = (metrics["compile_success"] / test_count) * 100
            metrics["spotbugs_success"] = (metrics["spotbugs_success"] / test_count) * 100
            metrics["key_success"] = (metrics["key_success"] / test_count) * 100

            # Compute average retries
            metrics["avg_retries"] = metrics["avg_retries"] / test_count

            # Average execution time
            metrics["avg_execution_time"] = metrics["execution_time"] / test_count

            print(f"\n📊 {model_name} Results:")
            print(f"  Success Rate: {metrics['success_rate']:.2f}%")
            print(f"  Compilation Success: {metrics['compile_success']:.2f}%")
            print(f"  SpotBugs Success: {metrics['spotbugs_success']:.2f}%")
            print(f"  KeY Success: {metrics['key_success']:.2f}%")
            print(f"  Average Retries: {metrics['avg_retries']:.2f}")
            print(f"  Average Execution Time: {metrics['avg_execution_time']:.2f} seconds")

    def _save_results(self):
        """
        Save evaluation results to disk in JSON format.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = os.path.join(self.output_dir, "data", f"evaluation_results_{timestamp}.json")

        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2)

        # Also save a CSV version for easy import into other tools
        csv_data = []
        for model_name, metrics in self.results["metrics"].items():
            for test_case in self.results["test_cases"]:
                test_result = metrics["test_results"].get(test_case, {})
                row = {
                    "model": model_name,
                    "test_case": test_case,
                    "success": test_result.get("success", False),
                    "compile_success": test_result.get("compile_success", False),
                    "spotbugs_success": test_result.get("spotbugs_success", False),
                    "key_success": test_result.get("key_success", False),
                    "retries": test_result.get("retries", 0),
                    "execution_time": test_result.get("execution_time", 0)
                }
                csv_data.append(row)

        df = pd.DataFrame(csv_data)
        csv_path = os.path.join(self.output_dir, "data", f"evaluation_results_{timestamp}.csv")
        df.to_csv(csv_path, index=False)

    def _generate_graphs(self):
        """
        Generate comprehensive visualization graphs based on the evaluation results.
        """
        # Prepare data for plotting
        models = list(self.results["metrics"].keys())
        success_rates = [self.results["metrics"][model]["success_rate"] for model in models]
        compile_rates = [self.results["metrics"][model]["compile_success"] for model in models]
        spotbugs_rates = [self.results["metrics"][model]["spotbugs_success"] for model in models]
        key_rates = [self.results["metrics"][model]["key_success"] for model in models]
        avg_retries = [self.results["metrics"][model]["avg_retries"] for model in models]
        avg_times = [self.results["metrics"][model].get("avg_execution_time", 
                                                        self.results["metrics"][model]["execution_time"] / 
                                                        len(self.results["test_cases"])
                                                        if len(self.results["test_cases"]) > 0 else 0) 
            for model in models]

        # Set up the style
        plt.style.use("ggplot")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        graph_dir = os.path.join(self.output_dir, "graphs")
        os.makedirs(graph_dir, exist_ok=True)

        # 1. Success Rate Comparison
        plt.figure(figsize=(12, 8))
        df = pd.DataFrame({
            "Model": models * 4,
            "Success Rate (%)": success_rates + compile_rates + spotbugs_rates + key_rates,
            "Metric": (["Overall Success"] * len(models) + 
                ["Compilation"] * len(models) + 
                ["SpotBugs"] * len(models) + 
                ["KeY Verification"] * len(models))
        })

        chart = sns.barplot(x="Model", y="Success Rate (%)", hue="Metric", data=df)
        chart.set_title("Success Rates by Model and Verification Method", fontsize=16)
        chart.set_ylim(0, 100)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(graph_dir, f"success_rates_{timestamp}.png"), dpi=300)

        # 2. Average Retries
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=models, y=avg_retries, palette="Blues_d")
        for i, value in enumerate(avg_retries):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", fontsize=10)
        plt.title("Average Retries by Model", fontsize=16)
        plt.xlabel("Model", fontsize=12)
        plt.ylabel("Average Retries", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(graph_dir, f"avg_retries_{timestamp}.png"), dpi=300)

        # 3. Average Execution Time
        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=models, y=avg_times, palette="Greens_d")
        for i, value in enumerate(avg_times):
            ax.text(i, value + 0.5, f"{value:.2f}s", ha="center", fontsize=10)
        plt.title("Average Execution Time by Model", fontsize=16)
        plt.xlabel("Model", fontsize=12)
        plt.ylabel("Time (seconds)", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(os.path.join(graph_dir, f"execution_time_{timestamp}.png"), dpi=300)

        # 4. Success Rate Radar Chart
        if len(models) > 1:
            plt.figure(figsize=(10, 8))

            # Create radar chart categories and values
            categories = ['Overall', 'Compilation', 'SpotBugs', 'KeY']
            N = len(categories)

            # Compute angle for each category
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]  # Close the loop

            # Initialize subplot
            ax = plt.subplot(111, polar=True)

            # Add each model as a line on the chart
            for i, model in enumerate(models):
                values = [
                    self.results["metrics"][model]["success_rate"],
                    self.results["metrics"][model]["compile_success"],
                    self.results["metrics"][model]["spotbugs_success"],
                    self.results["metrics"][model]["key_success"]
                ]
                values += values[:1]  # Close the loop

                # Plot values
                ax.plot(angles, values, linewidth=2, linestyle='solid', label=model)
                ax.fill(angles, values, alpha=0.1)

            # Set category labels
            plt.xticks(angles[:-1], categories)

            # Set radial limits
            plt.yticks([20, 40, 60, 80, 100], ['20%', '40%', '60%', '80%', '100%'], color='grey', size=10)
            plt.ylim(0, 100)

            # Add legend and title
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            plt.title('Success Metrics Comparison by Model', size=20, y=1.1)

            plt.tight_layout()
            plt.savefig(os.path.join(graph_dir, f"radar_chart_{timestamp}.png"), dpi=300)

        # 5. Detailed breakdown by test case (if we have multiple test cases)
        if len(self.results["test_cases"]) > 1:
            # Create a dataframe with test case results
            test_case_data = []
            for model_name in models:
                for test_case in self.results["test_cases"]:
                    test_result = self.results["metrics"][model_name]["test_results"].get(test_case, {})
                    test_case_data.append({
                        "Model": model_name,
                        "Test Case": test_case,
                        "Success": 100 if test_result.get("success", False) else 0
                    })

            df_test_cases = pd.DataFrame(test_case_data)

            plt.figure(figsize=(14, 8))
            chart = sns.barplot(x="Test Case", y="Success", hue="Model", data=df_test_cases)
            chart.set_title("Success by Test Case and Model", fontsize=16)
            chart.set_ylim(0, 100)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig(os.path.join(graph_dir, f"test_case_results_{timestamp}.png"), dpi=300)

            # 6. Heatmap of success by model and test case
            success_matrix = pd.pivot_table(
                df_test_cases, 
                values='Success', 
                index=['Model'], 
                columns=['Test Case'], 
                aggfunc='first'
            ).fillna(0)

            plt.figure(figsize=(12, 10))
            sns.heatmap(success_matrix, annot=True, cmap="YlGnBu", fmt=".0f", 
                        cbar_kws={'label': 'Success (%)'})
            plt.title("Success Rate Heatmap by Model and Test Case", fontsize=16)
            plt.tight_layout()
            plt.savefig(os.path.join(graph_dir, f"heatmap_{timestamp}.png"), dpi=300)

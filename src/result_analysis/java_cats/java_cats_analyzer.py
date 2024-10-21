# java_analyzer.py

from pathlib import Path
from result_analysis.base_analyzer import BaseAnalyzer
from result_analysis.utils import get_subdirs, do_sorted, load_json
from result_analysis.csv_writer import CSVWriter
from .java_cats_metrics import JavaMetrics  # Import the JavaMetrics class


class JavaAnalyzer(BaseAnalyzer):
    def __init__(
        self,
        results_dir,
        analysis_results_dir,
        analysis_metric=None,
        is_callsites=False,
    ):
        super().__init__(
            results_dir, analysis_results_dir, analysis_metric, is_callsites
        )

    def analyze(self):
        try:
            overall_data = {}
            for tool in sorted(get_subdirs(self.results_dir)):
                if tool == "analysis_results":
                    continue
                else:
                    tool_results_dir = Path(self.results_dir) / tool / "benchmarks"
                    analysis_results_file = (
                        Path(self.analysis_results_dir)
                        / f"{tool}_java_benchmark_eval.csv"
                    )
                    data = self.iterate_cats(tool_results_dir, analysis_results_file)
                    overall_data[tool] = data["total"]

            totals_csv = (
                Path(self.analysis_results_dir) / "totals_java_benchmark_eval.csv"
            )
            CSVWriter.write_totals_csv(totals_csv, overall_data)
            self.logger.info("Java Analysis completed.")
        except Exception as e:
            self.logger.error(f"Unexpected error during Java analysis: {e}")

    def iterate_cats(self, tool_results_dir, analysis_results_file):
        data = {}
        java_metrics = JavaMetrics(self.not_found_counter)  # Initialize JavaMetrics

        for cat in sorted(get_subdirs(tool_results_dir)):
            self.logger.info(f"Iterating through benchmark categories (Java)..")
            complete_passed = 0
            sound_passed = 0
            tests = get_subdirs(Path(tool_results_dir) / cat)
            cat_exact_matches = {"exact_matches": 0, "num_all": 0}

            for test in tests:
                self.logger.info(f"Analyzing Java test directory: {test}")
                test_path = Path(tool_results_dir) / cat / test
                _result_actual, _result_expected = self.data_loader(test_path)

                if java_metrics.equal_complete(_result_actual, _result_expected):
                    complete_passed += 1

                if java_metrics.equal_sound(_result_actual, _result_expected):
                    sound_passed += 1

                precision = java_metrics.measure_precision(
                    _result_actual, _result_expected
                )
                recall = java_metrics.measure_recall(_result_actual, _result_expected)
                exact_matches, num_all = java_metrics.measure_exact_matches(
                    _result_actual, _result_expected
                )

                cat_exact_matches["exact_matches"] += exact_matches
                cat_exact_matches["num_all"] += num_all

            data[cat] = {
                "complete": complete_passed,
                "sound": sound_passed,
                "all": len(tests),
                "exact_matches": cat_exact_matches["exact_matches"],
                "num_all": cat_exact_matches["num_all"],
            }

        return CSVWriter.write_category_csv(analysis_results_file, data)

    def data_loader(self, test):
        try:
            cg_path = Path(test) / "callgraph.json"
            results_path = Path(test) / "main_result.json"

            out_cg = load_json(results_path)
            expected_cg = load_json(cg_path)

            return out_cg, expected_cg
        except Exception as e:
            self.logger.error(
                f"Unexpected error in data_loader for Java test {test}: {e}"
            )
            return None, None

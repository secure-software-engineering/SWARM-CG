from pathlib import Path
from .metrics import Metrics
from .csv_writer import CSVWriter
from .utils import get_subdirs, do_sorted, load_json, setup_result_analysis_logging


class BaseAnalyzer:
    def __init__(
        self,
        results_dir,
        analysis_results_dir,
        analysis_metric=None,
        is_callsites=False,
    ):
        self.results_dir = results_dir
        self.analysis_results_dir = analysis_results_dir
        self.analysis_metric = (
            analysis_metric
            if analysis_metric
            else ["precision", "recall", "exact_matches", "complete", "sound"]
        )
        self.not_found_counter = []
        self.logger = setup_result_analysis_logging()
        self.is_callsites = is_callsites

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
                        / f"{tool}_micro_benchmark_eval.csv"
                    )
                    data = self.iterate_cats(tool_results_dir, analysis_results_file)
                    overall_data[tool] = data["total"]

            totals_csv = (
                Path(self.analysis_results_dir) / "totals_micro_benchmark_eval.csv"
            )
            CSVWriter.write_totals_csv(totals_csv, overall_data)
            self.logger.info("Analysis completed.")
        except Exception as e:
            self.logger.error(f"Unexpected error during analysis: {e}")

    def iterate_cats(self, tool_results_dir, analysis_results_file):
        metrics = Metrics(self.not_found_counter)
        data = {}

        for cat in sorted(get_subdirs(tool_results_dir)):
            self.logger.info(f"Iterating through benchmark categories..")
            complete_passed = 0
            sound_passed = 0
            tests = get_subdirs(Path(tool_results_dir) / cat)
            cat_exact_matches = {"exact_matches": 0, "num_all": 0}

            for test in tests:
                self.logger.info(f"Analyzing test directory: {test}")
                test_path = Path(tool_results_dir) / cat / test
                _result_actual, _result_expected = self.data_loader(
                    test_path, self.is_callsites
                )

                if metrics.equal_complete(_result_actual, _result_expected):
                    complete_passed += 1

                if metrics.equal_sound(_result_actual, _result_expected):
                    sound_passed += 1

                precision = metrics.measure_precision(_result_actual, _result_expected)
                recall = metrics.measure_recall(_result_actual, _result_expected)
                exact_matches, num_all = metrics.measure_exact_matches(
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

    def data_loader(self, test, is_callsites=False):
        """
        Load the expected and actual call graphs from test case directory.

        :param test: Path to the test case directory.
        :return: A tuple of (expected_callgraph, actual_callgraph)
        """
        try:
            if is_callsites:
                cg_path = Path(test) / "linesCallSite.json"
            else:
                cg_path = Path(test) / "callgraph.json"

            results_path = Path(test) / "main_result.json"

            out_cg = load_json(results_path)
            expected_cg = load_json(cg_path)

            return do_sorted(out_cg), do_sorted(expected_cg)
        except Exception as e:
            self.logger.error(f"Unexpected error in data_loader for test {test}: {e}")
            return None, None

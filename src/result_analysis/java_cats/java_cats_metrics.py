class JavaMetrics:
    def __init__(self, not_found_counter=[]):
        self.not_found_counter = not_found_counter

    def equal_sound(self, out, expected):
        for expected_item in expected:
            expected_callee_list = {
                callee["callee"] for callee in expected_item["targets"]
            }
            found = False
            for out_item in out:
                if out_item["caller"] == expected_item["caller"]:
                    out_callee_list = {
                        callee["callee"] for callee in out_item["targets"]
                    }
                    if not expected_callee_list.issubset(out_callee_list):
                        return False
                    found = True
                    break
            if not found:
                return False
        return True

    def equal_complete(self, out, expected):
        for out_item in out:
            out_callee_list = {callee["callee"] for callee in out_item["targets"]}
            found = False
            for expected_item in expected:
                if out_item["caller"] == expected_item["caller"]:
                    expected_callee_list = {
                        callee["callee"] for callee in expected_item["targets"]
                    }
                    if not out_callee_list.issubset(expected_callee_list):
                        return False
                    found = True
                    break
            if not found:
                return False
        return True

    def measure_precision(self, actual, expected):
        num_all = 0
        num_caught = 0

        for out_item in actual:
            actual_callees = {callee["callee"] for callee in out_item["targets"]}
            for expected_item in expected:
                if out_item["caller"] == expected_item["caller"]:
                    expected_callees = {
                        callee["callee"] for callee in expected_item["targets"]
                    }
                    num_all += len(actual_callees)
                    num_caught += len(actual_callees.intersection(expected_callees))

        if num_all == 0:
            num_all = 1

        return float(num_caught) / float(num_all)

    def measure_recall(self, actual, expected):
        num_all = 0
        num_caught = 0

        for expected_item in expected:
            expected_callees = {callee["callee"] for callee in expected_item["targets"]}
            for out_item in actual:
                if out_item["caller"] == expected_item["caller"]:
                    actual_callees = {
                        callee["callee"] for callee in out_item["targets"]
                    }
                    num_all += len(expected_callees)
                    num_caught += len(expected_callees.intersection(actual_callees))

        if num_all == 0:
            num_all = 1

        return float(num_caught) / float(num_all)

    def measure_exact_matches(self, actual, expected):
        num_all = 0
        num_exact_matches = 0

        for expected_item in expected:
            expected_callees = {callee["callee"] for callee in expected_item["targets"]}
            for out_item in actual:
                if out_item["caller"] == expected_item["caller"]:
                    actual_callees = {
                        callee["callee"] for callee in out_item["targets"]
                    }
                    num_all += len(expected_callees)
                    num_exact_matches += len(
                        expected_callees.intersection(actual_callees)
                    )

        if num_all == 0:
            num_all = 1

        return num_exact_matches, num_all

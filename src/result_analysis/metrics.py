class Metrics:
    def __init__(self, not_found_counter):
        self.not_found_counter = not_found_counter

    def equal_sound(self, out, expected):
        for item in expected:
            if item not in out:
                return False
            for edge in expected[item]:
                if edge not in out[item]:
                    return False
        return True

    def equal_complete(self, out, expected):
        for item in out:
            if item not in expected:
                continue
            for edge in out[item]:
                if edge not in expected[item]:
                    return False
        return True

    def measure_exact_matches(self, actual, expected):
        num_all = 0
        num_exact_matches = 0

        for node in expected:
            num_all += len(expected[node])
            for item in expected[node]:
                if actual.get(node, None) is None:
                    self.not_found_counter.append(item)
                    continue
                if item in actual[node]:
                    num_exact_matches += 1
                else:
                    self.not_found_counter.append(item)

        if num_all == 0:
            num_all = 1

        return num_exact_matches, num_all

    def measure_precision(self, actual, expected):
        num_all = 0
        num_caught = 0

        for node in actual:
            num_all += len(actual[node])
            for item in actual[node]:
                if expected.get(node, None) is None:
                    continue
                if item in expected[node]:
                    num_caught += 1

        if num_all == 0:
            num_all = 1

        return float(num_caught) / float(num_all)

    def measure_recall(self, actual, expected):
        num_all = 0
        num_caught = 0

        for node in expected:
            num_all += len(expected[node])
            for item in expected[node]:
                if actual.get(node, None) is None:
                    self.not_found_counter.append(item)
                    continue
                if item in actual[node]:
                    num_caught += 1
                else:
                    self.not_found_counter.append(item)

        if num_all == 0:
            num_all = 1

        return float(num_caught) / float(num_all)

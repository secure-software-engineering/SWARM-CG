import csv


class CSVWriter:
    @staticmethod
    def write_category_csv(res_file, data):
        header = [
            "Category",
            "Num-Cases",
            "Complete",
            "Sound",
            "Exact matches",
            "Num-all",
        ]
        total_num_cases = 0
        total_complete = 0
        total_sound = 0
        total_exact_matches = 0
        total_num_all = 0

        with open(res_file, "w+") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(header)

            for cat, values in sorted(data.items()):
                num_cases = values["all"]
                complete = values["complete"]
                sound = values["sound"]
                exact_matches = values["exact_matches"]
                num_all = values["num_all"]

                writer.writerow(
                    [cat, num_cases, complete, sound, exact_matches, num_all]
                )

                total_num_cases += num_cases
                total_complete += complete
                total_sound += sound
                total_exact_matches += exact_matches
                total_num_all += num_all

        data["total"] = {
            "total_num_cases": total_num_cases,
            "total_complete": total_complete,
            "total_sound": total_sound,
            "total_exact_matches": total_exact_matches,
            "total_num_all": total_num_all,
        }

        return data

    @staticmethod
    def write_totals_csv(totals_csv, overall_data):
        header = [
            "tool/model",
            "total_num_cases",
            "total_complete",
            "total_sound",
            "total_exact_matches",
            "total_num_all",
        ]

        with open(totals_csv, "w+") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(header)

            for model, data in sorted(
                overall_data.items(),
                key=lambda x: x[1]["total_exact_matches"],
                reverse=True,
            ):
                writer.writerow(
                    [
                        model,
                        data["total_num_cases"],
                        data["total_complete"],
                        data["total_sound"],
                        data["total_exact_matches"],
                        data["total_num_all"],
                    ]
                )

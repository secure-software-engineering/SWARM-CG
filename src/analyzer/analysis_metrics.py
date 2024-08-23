def calculate_metric(data, metric):
    if metric == "soundness":
        return calculate_soundness(data)
    elif metric == "completeness":
        return calculate_completeness(data)
    # Add other metrics as needed


def calculate_soundness(data):
    # Calculate and return soundness value
    return {"soundness_value": 0.95}


def calculate_completeness(data):
    # Calculate and return completeness value
    return {"completeness_value": 0.85}

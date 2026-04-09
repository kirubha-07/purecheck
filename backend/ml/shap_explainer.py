from typing import List, Dict
import numpy as np


def format_shap_explanation(
    shap_values: np.ndarray,
    feature_names: List[str],
    feature_values: np.ndarray,
    top_k: int = 5,
) -> Dict:
    """Format raw SHAP values into a compact API-friendly payload."""
    if shap_values is None or feature_names is None or feature_values is None:
        return {'base_value': 0.0, 'features': []}

    shap_array = np.asarray(shap_values, dtype=float)
    values_array = np.asarray(feature_values, dtype=float)

    explanation = {
        'base_value': float(np.mean(np.abs(shap_array))),
        'features': [],
    }

    indices = np.argsort(np.abs(shap_array))[::-1][:top_k]
    for idx in indices:
        if idx < len(feature_names) and idx < len(values_array):
            shap_value = float(shap_array[idx])
            explanation['features'].append(
                {
                    'name': feature_names[idx],
                    'value': float(values_array[idx]),
                    'shap_value': shap_value,
                    'impact': 'increases' if shap_value > 0 else 'decreases',
                }
            )

    return explanation

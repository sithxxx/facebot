"""
Normative facial-metric values, computed PER GENDER from a
gender-labeled dataset (tpremoli/CelebA-attrs) using the same metric
functions used at inference. Regenerate with recompute_norms.py.
"""

NORMS = {
    "male": {
        "face_symmetry": {"median": 0.9054, "std": 0.1233},
        "face_proportions": {"median": 0.8528, "std": 0.0950},
        "vertical_balance": {"median": 0.5771, "std": 0.1194},
        "jaw_cheek_balance": {"median": 1.0407, "std": 0.0176},
        "eye_size": {"median": 0.1881, "std": 0.0118},
        "eye_spacing": {"median": 0.2402, "std": 0.0159},
        "eye_tilt": {"median": 0.0665, "std": 0.0523},
        "nose_width": {"median": 0.2957, "std": 0.0226},
        "mouth_width": {"median": 0.3870, "std": 0.0525},
        "nose_length": {"median": 0.3659, "std": 0.0479},
        "chin_length": {"median": 0.2995, "std": 0.0394},
        "chin_contour": {"median": 0.4733, "std": 0.0636},
        "nose_to_mouth_ratio": {"median": 0.7663, "std": 0.0693},
        "biocular_width": {"median": 0.6157, "std": 0.0304},
        "forehead_width": {"median": 0.7608, "std": 0.0305},
        "lip_fullness": {"median": 0.3514, "std": 0.1539},
        "lip_proportions": {"median": 0.5449, "std": 0.1440},
        "jaw_to_mouth": {"median": 2.4901, "std": 0.3291},
        "eye_shape": {"median": 0.3226, "std": 0.0772},
        "brow_height": {"median": 0.6216, "std": 0.1679},
    },
    "female": {
        "face_symmetry": {"median": 0.9179, "std": 0.1119},
        "face_proportions": {"median": 0.8296, "std": 0.0587},
        "vertical_balance": {"median": 0.6152, "std": 0.1297},
        "jaw_cheek_balance": {"median": 1.0530, "std": 0.0163},
        "eye_size": {"median": 0.2002, "std": 0.0110},
        "eye_spacing": {"median": 0.2480, "std": 0.0159},
        "eye_tilt": {"median": 0.1120, "std": 0.0545},
        "nose_width": {"median": 0.2930, "std": 0.0222},
        "mouth_width": {"median": 0.4012, "std": 0.0605},
        "nose_length": {"median": 0.3809, "std": 0.0502},
        "chin_length": {"median": 0.2680, "std": 0.0335},
        "chin_contour": {"median": 0.4747, "std": 0.0463},
        "nose_to_mouth_ratio": {"median": 0.7238, "std": 0.0756},
        "biocular_width": {"median": 0.6428, "std": 0.0260},
        "forehead_width": {"median": 0.7867, "std": 0.0264},
        "lip_fullness": {"median": 0.4019, "std": 0.1098},
        "lip_proportions": {"median": 0.5542, "std": 0.1200},
        "jaw_to_mouth": {"median": 2.3556, "std": 0.3472},
        "eye_shape": {"median": 0.3482, "std": 0.0662},
        "brow_height": {"median": 0.6826, "std": 0.1377},
    },
}

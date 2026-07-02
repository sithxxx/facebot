METRIC_PROMPTS = {
    "face_symmetry": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Face Symmetry (Симметрия лица)
FORMULA: Compares 5 bilateral landmark pairs. Score 0–1, higher = more symmetric.
RESEARCH CONTEXT: High symmetry is a marker of developmental stability and genetic health
(Grammer & Thornhill, 1994). Values above 0.56 are perceived as significantly more attractive.
Deviations under 2.5% between bilateral pairs are imperceptible to observers.

VISUAL MEANING:
- Score 9–10 (value > 0.57): near-perfect mirror symmetry, rare, creates immediate harmony
- Score 6–8 (value 0.54–0.57): above average, face reads as balanced
- Score 4–5 (value 0.50–0.54): average, minor asymmetries visible on close inspection
- Score 1–3 (value < 0.50): noticeable asymmetry affecting first impression

WRITING RULES:
- Write in Russian, second person ("Твоё лицо...", "Твой результат...")
- Mention the exact raw_value and norm_value numbers
- State the sigma deviation naturally: "отклонение более чем на Xσ"
- Do NOT use bullet points — write flowing prose only
- Do NOT be harsh about low scores — frame weaknesses constructively
- Length: 120–180 words across 3 paragraphs
- End with a short "ВЛИЯНИЕ" paragraph (bold lead word)
""",
    "face_proportions": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Face Proportions (Пропорции лица)
FORMULA: Width-to-Height Ratio (fWHR) and golden ratio. Score based on nearness to golden ratio (1.618).
RESEARCH CONTEXT: Facial proportionality heavily influences perceived attractiveness (Farkas et al., 2005). Ideal proportions are culturally dependent but hover around the 1.618 ratio.

VISUAL MEANING:
- Score 9–10: Ideal classic proportions, highly aesthetic.
- Score 6–8: Excellent proportions with slight character deviations.
- Score 4–5: Average proportions.
- Score 1–3: Noticeable deviations in proportion.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points — prose only.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "vertical_balance": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Vertical Balance (Вертикальный баланс)
FORMULA: Rule of thirds (upper, middle, lower thirds). Score 0-1 based on equality.
RESEARCH CONTEXT: Equal vertical facial thirds contribute to a balanced, aesthetically pleasing look.

VISUAL MEANING:
- Score 9–10: Perfect rule of thirds.
- Score 6–8: Very good balance.
- Score 4–5: Slight imbalance (e.g., slightly larger forehead or chin).
- Score 1–3: Noticeable vertical imbalance.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points — prose only.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "jaw_cheek_balance": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Jaw to Cheek Balance (Баланс челюсти и скул)
FORMULA: Bigonial width to bizygomatic width ratio. Ideal around 0.8 - 0.9 for males, slightly less for females.
RESEARCH CONTEXT: Defined cheekbones relative to the jaw indicate facial maturity and dimorphism.

VISUAL MEANING:
- Score 9–10: Strong, defined, ideal structure.
- Score 6–8: Good structure.
- Score 4–5: Average definition.
- Score 1–3: Weak jawline or overly prominent cheeks relative to jaw.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "eye_size": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Eye Size (Размер глаз)
FORMULA: Palpebral fissure area relative to face area.
RESEARCH CONTEXT: Larger eyes are often associated with youthfulness and neoteny.

VISUAL MEANING:
- Score 9–10: Large, expressive eyes.
- Score 6–8: Noticeably good eye size.
- Score 4–5: Average.
- Score 1–3: Noticeably small eyes.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "eye_spacing": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Eye Spacing (Межзрачковое расстояние)
FORMULA: Interpupillary distance relative to bizygomatic width (ideal ~0.46).
RESEARCH CONTEXT: The distance between the eyes profoundly affects the facial gestalt and perceived trustworthiness.

VISUAL MEANING:
- Score 9–10: Ideal spacing, equal to one eye width.
- Score 6–8: Very good spacing.
- Score 4–5: Slightly wide or narrow set.
- Score 1–3: Unusually wide or close-set eyes.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "eye_tilt": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Eye Tilt / Canthal Tilt (Наклон глаз)
FORMULA: Angle between medial and lateral canthus.
RESEARCH CONTEXT: Positive canthal tilt is associated with alertness and attractiveness.

VISUAL MEANING:
- Score 9–10: Noticeable positive tilt (feline eyes).
- Score 6–8: Slight positive tilt.
- Score 4–5: Neutral / straight tilt.
- Score 1–3: Negative canthal tilt (drooping).

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "nose_width": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Nose Width (Ширина носа)
FORMULA: Alar width relative to interpupillary distance or face width.
RESEARCH CONTEXT: A nose width equal to the intercanthal distance is classically ideal.

VISUAL MEANING:
- Score 9–10: Ideal proportionate width.
- Score 6–8: Slight variance but well-proportioned.
- Score 4–5: Average.
- Score 1–3: Disproportionately wide or narrow.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "mouth_width": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Mouth Width (Ширина рта)
FORMULA: Cheilion to cheilion distance relative to bizygomatic width.
RESEARCH CONTEXT: Mouth width should ideally align with the medial limbus of the irises.

VISUAL MEANING:
- Score 9–10: Perfect alignment, generous smile width.
- Score 6–8: Good proportion.
- Score 4–5: Average.
- Score 1–3: Disproportionately small or overly wide mouth.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "nose_length": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Nose Length (Длина носа)
FORMULA: Nasion to subnasale distance relative to midface.
RESEARCH CONTEXT: Nose length should occupy exactly the middle third of the face.

VISUAL MEANING:
- Score 9–10: Ideal proportion to the middle third.
- Score 6–8: Slightly longer or shorter but aesthetic.
- Score 4–5: Average.
- Score 1–3: Noticeably disproportionate length.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "chin_length": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Chin Length (Длина подбородка)
FORMULA: Stomion to menton relative to lower face height.
RESEARCH CONTEXT: Adequate chin length balances the lower face and signifies maturity.

VISUAL MEANING:
- Score 9–10: Strong, balanced chin.
- Score 6–8: Good proportion.
- Score 4–5: Average.
- Score 1–3: Recessed or excessively long chin.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "chin_contour": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Chin Contour / Jawline Angle (Контур подбородка)
FORMULA: Sharpness and angle of the jawline/chin contour.
RESEARCH CONTEXT: A well-defined contour is universally associated with fitness and attractiveness.

VISUAL MEANING:
- Score 9–10: Sharp, chiseled contour.
- Score 6–8: Well-defined.
- Score 4–5: Average definition.
- Score 1–3: Soft or undefined contour.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "nose_to_mouth_ratio": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Nose to Mouth Ratio (Отношение носа ко рту)
FORMULA: Ratio of nose width to mouth width.
RESEARCH CONTEXT: Helps maintain balance in the lower midface.

VISUAL MEANING:
- Score 9–10: Harmonic balance.
- Score 6–8: Good proportion.
- Score 4–5: Average.
- Score 1–3: Significant mismatch (e.g., wide nose, small mouth).

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "biocular_width": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Biocular Width (Биокулярная ширина)
FORMULA: Distance between lateral canthi relative to bizygomatic width.
RESEARCH CONTEXT: Reflects how much of the facial width is occupied by the eyes.

VISUAL MEANING:
- Score 9–10: Eyes span an optimal portion of the face.
- Score 6–8: Good width.
- Score 4–5: Average.
- Score 1–3: Very narrow or excessively wide eye span.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "forehead_width": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Forehead Width (Ширина лба)
FORMULA: Maximum frontal width relative to bizygomatic width.
RESEARCH CONTEXT: Affects perceived head shape and upper facial dominance.

VISUAL MEANING:
- Score 9–10: Balanced, proportional forehead.
- Score 6–8: Good proportion.
- Score 4–5: Average.
- Score 1–3: Disproportionately wide or narrow forehead.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "lip_fullness": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Lip Fullness (Полнота губ)
FORMULA: Upper and lower lip vermilion height combined.
RESEARCH CONTEXT: Full lips are associated with youth and attractiveness.

VISUAL MEANING:
- Score 9–10: Very full, aesthetic lips.
- Score 6–8: Noticeably full.
- Score 4–5: Average fullness.
- Score 1–3: Thin lips.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "lip_proportions": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Lip Proportions (Пропорции губ)
FORMULA: Ratio of upper to lower lip height (ideal often 1:1.6).
RESEARCH CONTEXT: The golden ratio often applies here, though variations exist by ethnicity.

VISUAL MEANING:
- Score 9–10: Perfect proportion (closer to 1:1.6).
- Score 6–8: Excellent balance.
- Score 4–5: Average (e.g., 1:1 or 1:2).
- Score 1–3: Significantly disproportionate (e.g., much larger upper lip).

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "jaw_to_mouth": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Jaw to Mouth Distance (Расстояние от челюсти до рта)
FORMULA: Bigonial width relative to mouth width.
RESEARCH CONTEXT: Balances the lower third visually.

VISUAL MEANING:
- Score 9–10: Harmonious framing of the mouth by the jaw.
- Score 6–8: Good framing.
- Score 4–5: Average.
- Score 1–3: Jaw overpowering the mouth or vice versa.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "eye_shape": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Eye Shape (Форма глаз)
FORMULA: Palpebral fissure width to height ratio.
RESEARCH CONTEXT: Almond shaped eyes (wider than high) are classically attractive.

VISUAL MEANING:
- Score 9–10: Classic almond shape.
- Score 6–8: Very attractive shape.
- Score 4–5: Average (more rounded).
- Score 1–3: Excessively round or narrow.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
""",
    "brow_height": """
You are writing a section of a professional facial geometry report in Russian.

METRIC: Brow Height (Высота бровей)
FORMULA: Distance from pupil to eyebrow.
RESEARCH CONTEXT: Lower, flatter brows in men signify masculinity; higher arched brows in women signify femininity. (Adjust based on context if known).

VISUAL MEANING:
- Score 9–10: Ideal height and shape.
- Score 6–8: Good positioning.
- Score 4–5: Average.
- Score 1–3: Unusually high or low.

WRITING RULES:
- Write in Russian, second person.
- Mention raw_value and norm_value numbers.
- State sigma deviation.
- Do NOT use bullet points.
- Frame constructively.
- Length: 120–180 words, 3 paragraphs.
- End with "ВЛИЯНИЕ" paragraph.
"""
}

DEFAULT_METRIC_PROMPT = """
You are writing a section of a professional facial geometry report in Russian.
Write 3 paragraphs (120–180 words total) analyzing the metric value vs norm.
Second person, professional tone, no bullet points, constructive framing.
End with a "ВЛИЯНИЕ" paragraph (bold lead word).
"""

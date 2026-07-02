import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import base64
from io import BytesIO
import scipy.stats as stats

from face_analysis.models import MetricResult

def score_to_color(score: float) -> str:
    """Maps score 1–10 to hex color."""
    if score >= 9:
        return "#F5A623" # gold
    elif score >= 7:
        return "#1D9E75" # green
    elif score >= 5:
        return "#4A90D9" # blue
    elif score >= 3:
        return "#9B59B6" # purple
    else:
        return "#E74C3C" # red

def _fig_to_base64(fig) -> str:
    """Helper to convert a matplotlib figure to base64 string."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', transparent=True, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode('utf-8')

def generate_radar_chart(metrics: list[MetricResult]) -> str:
    """Creates a radar/spider chart of all 20 metric scores."""
    labels = [m.name_ru for m in metrics]
    scores = [m.score for m in metrics]
    num_vars = len(labels)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    # Complete the loop
    scores += scores[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), facecolor='#0D0D0D')
    
    # Plot data
    ax.plot(angles, scores, color='#8B5CF6', linewidth=1.5, zorder=10)
    
    # Fill area
    ax.fill(angles, scores, color='#06B6D4', alpha=0.25, zorder=5)
    
    # Set y-axis
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels([])
    
    # Set x-axis
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='#9CA3AF', fontsize=7)
    
    # Grid styling
    ax.grid(color='#2A2A2A', linewidth=0.5)
    ax.spines['polar'].set_color('#2A2A2A')
    ax.set_facecolor('#0D0D0D')
    
    return _fig_to_base64(fig)

def generate_score_bar(score: float, color: str) -> str:
    """Creates a horizontal progress bar image for a single metric score."""
    width = 300
    height = 8
    
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    ax.axis('off')
    
    # Background bar
    bg_rect = mpatches.Rectangle((0, 0), 10, 1, facecolor='#1F1F1F')
    ax.add_patch(bg_rect)
    
    # Filled bar
    fill_rect = mpatches.Rectangle((0, 0), score, 1, facecolor=color)
    ax.add_patch(fill_rect)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 1)
    
    return _fig_to_base64(fig)

def generate_bell_curve(sigma_deviation: float) -> str:
    """Creates a bell curve showing where user sits in population."""
    fig, ax = plt.subplots(figsize=(4, 2), dpi=100, facecolor='#0D0D0D')
    ax.set_facecolor('#0D0D0D')
    ax.axis('off')
    
    # Generate normal distribution curve
    x = np.linspace(-3.5, 3.5, 100)
    y = stats.norm.pdf(x, 0, 1)
    
    ax.plot(x, y, color='#9CA3AF', linewidth=1)
    
    # Fill color based on position
    if sigma_deviation > 1:
        fill_color = '#1D9E75'  # Green
    elif sigma_deviation >= -1:
        fill_color = '#F5A623'  # Amber/Gold
    else:
        fill_color = '#E74C3C'  # Red
        
    ax.fill_between(x, y, alpha=0.1, color='#9CA3AF')
    
    # Add vertical line for user's position
    clamped_sigma = max(min(sigma_deviation, 3.5), -3.5)
    y_val = stats.norm.pdf(clamped_sigma, 0, 1)
    ax.vlines(clamped_sigma, 0, y_val, colors=fill_color, linewidth=2, zorder=5)
    
    ax.set_ylim(0, 0.45)
    
    return _fig_to_base64(fig)

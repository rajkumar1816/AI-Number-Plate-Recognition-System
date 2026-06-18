from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


def plot_bar_chart(data_frame: pd.DataFrame, x_column: str, y_column: str, title: str) -> Any:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(data_frame[x_column], data_frame[y_column], color="#2563eb")
    ax.set_title(title)
    ax.set_xlabel(x_column.replace("_", " ").title())
    ax.set_ylabel(y_column.replace("_", " ").title())
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    return fig


def plot_line_chart(data_frame: pd.DataFrame, x_column: str, y_column: str, title: str) -> Any:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data_frame[x_column], data_frame[y_column], marker="o", color="#10b981")
    ax.set_title(title)
    ax.set_xlabel(x_column.replace("_", " ").title())
    ax.set_ylabel(y_column.replace("_", " ").title())
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    return fig

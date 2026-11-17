"""Create a dataset overview and a depth-based well-log plot for train.csv."""

import argparse
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, Normalize


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
LITHOLOGY_COLUMN = "FORCE_2020_LITHOFACIES_LITHOLOGY"
LOG_COLUMNS = ["GR", "RDEP", "RMED", "RSHA", "RHOB", "NPHI", "DTC", "PEF"]
SCAN_COLUMNS = ["WELL", LITHOLOGY_COLUMN, *LOG_COLUMNS]
PROFILE_COLUMNS = ["WELL", "DEPTH_MD", LITHOLOGY_COLUMN, *LOG_COLUMNS]
TRACKS = [
    ("GR", "Gamma ray (GR)"),
    ("RESISTIVITY", "Resistivity"),
    ("RHOB", "Bulk density (RHOB)"),
    ("NPHI", "Neutron porosity (NPHI)"),
    ("DTC", "Sonic travel time (DTC)"),
    ("PEF", "Photoelectric factor (PEF)"),
]


def scan_dataset(path: Path) -> tuple[Counter, Counter, Counter, int]:
    """Collect well counts, lithology counts, and log missingness in chunks."""
    header = pd.read_csv(path, sep=";", nrows=0).columns
    required = set(SCAN_COLUMNS + ["DEPTH_MD"])
    missing_columns = required.difference(header)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{path} is missing required columns: {missing}")

    well_counts: Counter = Counter()
    lithology_counts: Counter = Counter()
    missing_counts: Counter = Counter()
    total_rows = 0

    for chunk in pd.read_csv(path, sep=";", usecols=SCAN_COLUMNS, chunksize=100_000):
        total_rows += len(chunk)
        well_counts.update(chunk["WELL"].value_counts().to_dict())
        lithology_counts.update(chunk[LITHOLOGY_COLUMN].value_counts().to_dict())
        missing_counts.update(chunk[LOG_COLUMNS].isna().sum().to_dict())

    if total_rows == 0:
        raise ValueError(f"{path} contains no data rows.")
    return well_counts, lithology_counts, missing_counts, total_rows


def load_well(path: Path, well: str) -> pd.DataFrame:
    """Read only one well from the large training CSV."""
    pieces = []
    for chunk in pd.read_csv(path, sep=";", usecols=PROFILE_COLUMNS, chunksize=100_000):
        selected = chunk.loc[chunk["WELL"] == well]
        if not selected.empty:
            pieces.append(selected)

    if not pieces:
        raise ValueError(f"No records found for well {well!r} in {path}.")

    data = pd.concat(pieces, ignore_index=True)
    data["DEPTH_MD"] = pd.to_numeric(data["DEPTH_MD"], errors="raise")
    for column in LOG_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="raise")
    return data.dropna(subset=["DEPTH_MD"]).sort_values("DEPTH_MD")


def plot_overview(
    well_counts: Counter,
    lithology_counts: Counter,
    missing_counts: Counter,
    total_rows: int,
    output_path: Path,
) -> None:
    """Plot lithology class balance and missing log measurements."""
    class_codes = sorted(lithology_counts)
    palette = plt.get_cmap("tab20").colors
    class_colors = {
        code: palette[index % len(palette)]
        for index, code in enumerate(class_codes)
    }

    fig, (class_axis, missing_axis) = plt.subplots(
        1, 2, figsize=(14, 7), constrained_layout=True
    )
    class_items = sorted(lithology_counts.items(), key=lambda item: item[1])
    class_axis.barh(
        [str(int(code)) for code, _ in class_items],
        [count for _, count in class_items],
        color=[class_colors[code] for code, _ in class_items],
    )
    class_axis.set_xscale("log")
    class_axis.set_xlabel("Rows (log scale)")
    class_axis.set_ylabel("Lithology code")
    class_axis.set_title("Lithology class distribution")
    class_axis.grid(axis="x", alpha=0.25)

    missing_percent = {
        column: 100 * missing_counts[column] / total_rows
        for column in LOG_COLUMNS
    }
    missing_items = sorted(missing_percent.items(), key=lambda item: item[1])
    missing_axis.barh(
        [column for column, _ in missing_items],
        [percent for _, percent in missing_items],
        color="#64748b",
    )
    missing_axis.set_xlabel("Missing rows (%)")
    missing_axis.set_title("Missing log measurements")
    missing_axis.set_xlim(0, 100)
    missing_axis.grid(axis="x", alpha=0.25)
    for index, (_, percent) in enumerate(missing_items):
        missing_axis.text(percent + 1, index, f"{percent:.1f}%", va="center")

    fig.suptitle(
        f"Training data overview: {total_rows:,} rows, {len(well_counts)} wells"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved dataset overview to {output_path}")


def plot_well_profile(
    data: pd.DataFrame,
    well: str,
    lithology_counts: Counter,
    output_path: Path,
    show: bool,
) -> None:
    """Plot standard log tracks and lithology against measured depth."""
    class_codes = sorted(lithology_counts)
    palette = plt.get_cmap("tab20").colors
    cmap = ListedColormap(
        [palette[index % len(palette)] for index in range(len(class_codes))]
    )
    norm = Normalize(vmin=-0.5, vmax=len(class_codes) - 0.5)

    fig, axes = plt.subplots(
        1,
        7,
        figsize=(18, 10),
        sharey=True,
        gridspec_kw={"width_ratios": [1, 1.5, 1, 1, 1, 1, 0.22]},
        constrained_layout=True,
    )
    depth = data["DEPTH_MD"]

    axis = axes[0]
    axis.plot(data["GR"], depth, color="#15803d", linewidth=0.65)
    axis.set_title("Gamma ray")
    axis.set_xlabel("API")

    axis = axes[1]
    for column, color in (("RSHA", "#7c3aed"), ("RMED", "#2563eb"), ("RDEP", "#dc2626")):
        values = data[column].where(data[column] > 0)
        axis.plot(values, depth, label=column, color=color, linewidth=0.65)
    axis.set_xscale("log")
    axis.set_title("Resistivity")
    axis.set_xlabel("Ohm·m")
    axis.legend(loc="best", fontsize="x-small")

    for axis, column, title, color in (
        (axes[2], "RHOB", "Bulk density", "#92400e"),
        (axes[3], "NPHI", "Neutron porosity", "#0891b2"),
        (axes[4], "DTC", "Sonic", "#c026d3"),
        (axes[5], "PEF", "Photoelectric factor", "#ea580c"),
    ):
        axis.plot(data[column], depth, color=color, linewidth=0.65)
        axis.set_title(title)
        axis.set_xlabel(column)

    axes[0].set_ylabel("Measured depth")

    class_indices = pd.Categorical(
        data[LITHOLOGY_COLUMN], categories=class_codes
    ).codes
    valid_classes = class_indices >= 0
    axes[6].scatter(
        np.zeros(valid_classes.sum()),
        depth[valid_classes],
        c=class_indices[valid_classes],
        cmap=cmap,
        norm=norm,
        marker="s",
        s=12,
        linewidths=0,
    )
    axes[6].set_title("Lithology")
    axes[6].set_xticks([])
    colorbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap=cmap),
        ax=axes[6],
        ticks=range(len(class_codes)),
        pad=0.03,
    )
    colorbar.ax.set_yticklabels([str(int(code)) for code in class_codes])
    colorbar.set_label("Lithology code")

    for axis in axes:
        axis.set_ylim(depth.max(), depth.min())
        axis.grid(axis="x", alpha=0.2)
        axis.tick_params(axis="x", labelrotation=25, labelsize=8)

    fig.suptitle(f"Well log profile: {well} ({len(data):,} depth samples)")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    print(f"Saved well profile to {output_path}")
    if show:
        plt.show()
    else:
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH, help="Semicolon-delimited train.csv")
    parser.add_argument(
        "--well",
        help="Well name to plot; defaults to the well with the most rows",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs",
        help="Directory for generated PNG files",
    )
    parser.add_argument("--no-show", action="store_true", help="Save charts without opening windows")
    args = parser.parse_args()

    well_counts, lithology_counts, missing_counts, total_rows = scan_dataset(args.data)
    well = args.well or well_counts.most_common(1)[0][0]
    if well not in well_counts:
        raise ValueError(f"Unknown well {well!r}; found {len(well_counts)} wells in {args.data}.")

    plot_overview(
        well_counts,
        lithology_counts,
        missing_counts,
        total_rows,
        args.output_dir / "train_data_overview.png",
    )
    well_data = load_well(args.data, well)
    plot_well_profile(
        well_data,
        well,
        lithology_counts,
        args.output_dir / f"well_log_{well.replace('/', '_').replace(' ', '_')}.png",
        show=not args.no_show,
    )


if __name__ == "__main__":
    main()

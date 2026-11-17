"""Visualize daily production and well contributions from the Volve dataset."""

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "production_data_processed.csv"
VOLUME_COLUMNS = {
    "BORE_OIL_VOL": ("Oil production", "#2563eb"),
    "BORE_GAS_VOL": ("Gas production", "#16a34a"),
    "BORE_WAT_VOL": ("Water production", "#0891b2"),
}
REQUIRED_COLUMNS = {"DATEPRD", "WELL_BORE_CODE", *VOLUME_COLUMNS}


def load_data(path: Path) -> pd.DataFrame:
    """Load production records and validate the columns used by the plots."""
    data = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{path} is missing required columns: {missing}")
    if data.empty:
        raise ValueError(f"{path} contains no production records.")

    data["DATEPRD"] = pd.to_datetime(data["DATEPRD"], errors="raise")
    for column in VOLUME_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="raise")
    return data


def _format_date_axis(axis: plt.Axes) -> None:
    locator = mdates.AutoDateLocator()
    axis.xaxis.set_major_locator(locator)
    axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def plot_production(
    data: pd.DataFrame,
    output_path: Path,
    well_output_path: Path,
    show: bool = True,
) -> None:
    """Plot field totals and production trends for each well."""
    calendar = pd.date_range(data["DATEPRD"].min(), data["DATEPRD"].max(), freq="D")
    daily = (
        data.groupby("DATEPRD")[list(VOLUME_COLUMNS)]
        .sum()
        .sort_index()
        .reindex(calendar)
    )
    wells_with_data = (
        data.groupby("DATEPRD")["WELL_BORE_CODE"]
        .nunique()
        .reindex(calendar, fill_value=0)
    )
    rolling = daily.rolling("30D", min_periods=1).mean()

    fig, axes = plt.subplots(2, 2, figsize=(15, 9), constrained_layout=True)
    time_axes = (axes[0, 0], axes[0, 1], axes[1, 0])

    for axis, (column, (label, color)) in zip(time_axes, VOLUME_COLUMNS.items()):
        axis.plot(
            calendar,
            daily[column],
            color=color,
            linewidth=0.8,
            alpha=0.25,
            label="Daily reported total",
        )
        axis.plot(
            calendar,
            rolling[column],
            color=color,
            linewidth=1.8,
            label="30-day mean (reported days)",
        )
        axis.set_title(label)
        axis.set_ylabel("Daily volume")
        axis.grid(True, alpha=0.25)
        _format_date_axis(axis)

    time_axes[0].legend(loc="upper right", fontsize="small")

    coverage_axis = axes[1, 1]
    coverage_axis.step(calendar, wells_with_data, where="mid", color="#6b7280")
    coverage_axis.set_title("Daily well-record coverage")
    coverage_axis.set_ylabel("Wells with records")
    coverage_axis.set_ylim(-0.25, data["WELL_BORE_CODE"].nunique() + 0.5)
    coverage_axis.set_yticks(range(data["WELL_BORE_CODE"].nunique() + 1))
    coverage_axis.grid(True, alpha=0.25)
    _format_date_axis(coverage_axis)

    well_order = (
        data.groupby("WELL_BORE_CODE")["BORE_OIL_VOL"]
        .sum()
        .sort_values(ascending=False)
        .index
    )
    well_daily = (
        data.groupby(["WELL_BORE_CODE", "DATEPRD"])[list(VOLUME_COLUMNS)]
        .sum()
        .sort_index()
    )
    well_count = len(well_order)
    well_fig, well_axes = plt.subplots(
        well_count,
        len(VOLUME_COLUMNS),
        figsize=(16, max(7, 2.2 * well_count)),
        sharex="col",
        squeeze=False,
        constrained_layout=True,
    )

    for row, well in enumerate(well_order):
        well_series = well_daily.xs(well, level="WELL_BORE_CODE").reindex(calendar)
        well_rolling = well_series.rolling("30D", min_periods=1).mean()
        for column_index, (column, (label, color)) in enumerate(VOLUME_COLUMNS.items()):
            axis = well_axes[row, column_index]
            axis.plot(calendar, well_series[column], color=color, linewidth=0.7, alpha=0.25)
            axis.plot(calendar, well_rolling[column], color=color, linewidth=1.5)
            axis.grid(True, alpha=0.25)
            if row == 0:
                axis.set_title(label)
                axis.legend(["Daily reported", "30-day mean"], loc="upper right", fontsize="x-small")
            if column_index == 0:
                axis.set_ylabel(f"{well}\nVolume")
            if row == well_count - 1:
                _format_date_axis(axis)

    well_fig.suptitle("Daily and 30-Day Average Production by Well")
    well_fig.supxlabel("Date")

    start_date = calendar.min().strftime("%Y-%m-%d")
    end_date = calendar.max().strftime("%Y-%m-%d")
    fig.suptitle(f"Volve Field Production Overview ({start_date} to {end_date})")

    for figure, path in ((fig, output_path), (well_fig, well_output_path)):
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=160, bbox_inches="tight")
        print(f"Saved visualization to {path}")

    if show:
        plt.show()
    else:
        plt.close(fig)
        plt.close(well_fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=DATA_PATH,
        help="Path to production_data_processed.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "production_overview.png",
        help="Path for the saved chart image",
    )
    parser.add_argument(
        "--well-output",
        type=Path,
        default=PROJECT_ROOT / "outputs" / "production_by_well.png",
        help="Path for the per-well chart image",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Save the chart without opening a plot window",
    )
    args = parser.parse_args()

    data = load_data(args.data)
    plot_production(data, args.output, args.well_output, show=not args.no_show)


if __name__ == "__main__":
    main()
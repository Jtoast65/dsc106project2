import os
import sys
from pathlib import Path

LOCAL_DEPS = Path(__file__).resolve().parent / ".local_deps"
if LOCAL_DEPS.exists():
    sys.path.insert(0, str(LOCAL_DEPS))

MPLCONFIGDIR = Path(__file__).resolve().parent / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parent
DATASET_PATH = next(ROOT.glob("dataset_*.csv"))
OUTPUT_PDF = ROOT / "checkpoint_submission.pdf"

PROPOSITION = "Advanced economies have made meaningful progress in reducing greenhouse gas emissions since 2010."
LEANING = "We lean toward the proposition being moderately true overall, although the progress is uneven and heavily concentrated in the electricity sector."


def load_annual_series():
    df = pd.read_csv(DATASET_PATH)
    annual_cols = [col for col in df.columns if col.isdigit()]

    subset = df[
        (df["COUNTRY"] == "Advanced Economies")
        & (df["FREQUENCY"] == "Annual")
        & (df["GAS_TYPE"] == "Greenhouse gas")
    ][["INDUSTRY"] + annual_cols].copy()

    subset = subset.dropna(subset=["2010", "2023"], how="any")
    subset = subset.set_index("INDUSTRY")
    return subset, annual_cols


def format_mtco2(value):
    return f"{value / 1000:.1f}B"


def apply_common_style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.labelcolor": "#23313d",
            "axes.edgecolor": "#c7d0d9",
            "xtick.color": "#4f5f6f",
            "ytick.color": "#4f5f6f",
            "text.color": "#23313d",
        }
    )


def add_card(ax):
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_visible(False)
    patch = FancyBboxPatch(
        (0, 0),
        1,
        1,
        transform=ax.transAxes,
        boxstyle="round,pad=0.012,rounding_size=16",
        linewidth=1.1,
        edgecolor="#d6dde5",
        facecolor="white",
        zorder=-10,
    )
    ax.add_patch(patch)


def add_chart_header(ax, title, subtitle, title_size=15, subtitle_size=10.5, title_y=1.035, subtitle_y=1.0):
    ax.text(
        0.0,
        title_y,
        title,
        transform=ax.transAxes,
        fontsize=title_size,
        fontweight="bold",
        color="#23313d",
        ha="left",
        va="bottom",
    )
    ax.text(
        0.0,
        subtitle_y,
        subtitle,
        transform=ax.transAxes,
        fontsize=subtitle_size,
        color="#5a6a79",
        ha="left",
        va="bottom",
    )


def save_page_as_png(fig, name):
    fig.savefig(ROOT / name, dpi=220, bbox_inches="tight")


def make_true_page(annual):
    years = [int(col) for col in annual.columns if col <= "2023"]
    year_labels = [str(year) for year in years]
    total = annual.loc["Total Industries + Total Households", year_labels]
    sectors = annual.drop(index="Total Industries + Total Households")
    pct_change = ((sectors["2023"] - sectors["2010"]) / sectors["2010"] * 100).sort_values()

    fig = plt.figure(figsize=(8.5, 11), facecolor="#f4f7f9")
    gs = fig.add_gridspec(12, 6, left=0.05, right=0.97, top=0.94, bottom=0.05, hspace=0.72, wspace=0.45)

    ax1 = fig.add_subplot(gs[:5, :])
    add_card(ax1)
    ax1.grid(axis="y", color="#e7edf2", linewidth=1)
    ax1.set_axisbelow(True)
    ax1.plot(years, total.values, color="#1f7a5a", linewidth=3.5)
    ax1.fill_between(years, total.values, [0] * len(years), color="#7bc8a4", alpha=0.16)
    ax1.scatter([2010, 2023], [total["2010"], total["2023"]], color="#1f7a5a", s=48, zorder=3)
    ax1.set_xlim(2010, 2023)
    ax1.set_ylim(0, max(total.values) * 1.12)
    add_chart_header(
        ax1,
        "Economy-wide emissions fell 15.5% from 2010 to 2023",
        "Annual greenhouse-gas emissions for Advanced Economies, all industries plus households.",
    )
    ax1.set_ylabel("Metric tons of CO2 equivalent")
    ax1.set_xticks([2010, 2013, 2016, 2019, 2023])
    ax1.set_yticks([0, 4000, 8000, 12000, 16000])
    ax1.set_yticklabels(["0", "4B", "8B", "12B", "16B"])
    ax1.annotate(
        "15.7B in 2010",
        xy=(2010, total["2010"]),
        xytext=(2011.1, total["2010"] + 950),
        arrowprops={"arrowstyle": "-", "color": "#6f8190"},
        fontsize=10,
        color="#455867",
    )
    ax1.annotate(
        "13.2B in 2023",
        xy=(2023, total["2023"]),
        xytext=(2019.3, total["2023"] + 850),
        arrowprops={"arrowstyle": "-", "color": "#6f8190"},
        fontsize=10,
        color="#455867",
    )
    ax1.text(
        0.98,
        0.08,
        "By 2023, annual emissions remain about\n2.4B tons below their 2010 level.",
        transform=ax1.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color="#35596e",
        bbox={"boxstyle": "round,pad=0.35", "fc": "#edf8f2", "ec": "#b6dec9"},
    )

    ax2 = fig.add_subplot(gs[6:, :])
    add_card(ax2)
    colors = ["#2e8b57" if value < 0 else "#c6d0d9" for value in pct_change.values]
    ax2.barh(pct_change.index, pct_change.values, color=colors, edgecolor="none", height=0.62)
    ax2.axvline(0, color="#8ea0af", linewidth=1)
    ax2.grid(axis="x", color="#e7edf2")
    ax2.set_axisbelow(True)
    add_chart_header(
        ax2,
        "Most major sectors moved downward over the same period",
        "Percent change in annual greenhouse-gas emissions by sector, 2010 to 2023.",
    )
    ax2.set_xlabel("Percent change since 2010")
    ax2.set_xlim(min(pct_change.values) - 8, max(pct_change.values) + 10)

    for y, value in enumerate(pct_change.values):
        label = f"{value:+.1f}%"
        align = "right" if value < 0 else "left"
        offset = -1.5 if value < 0 else 1.5
        ax2.text(value + offset, y, label, va="center", ha=align, fontsize=10, color="#23313d")

    ax2.text(
        0.98,
        0.07,
        "The largest declines come from electricity,\nother services, and manufacturing.",
        transform=ax2.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color="#35596e",
        bbox={"boxstyle": "round,pad=0.35", "fc": "#edf8f2", "ec": "#b6dec9"},
    )

    save_page_as_png(fig, "checkpoint_page_1_true.png")
    return fig


def make_false_page(annual):
    comparison_years = [str(year) for year in range(2015, 2024)]
    focus_sectors = [
        "Transportation and Storage",
        "Total Households",
        "Agriculture, Forestry and Fishing",
    ]

    fig = plt.figure(figsize=(8.5, 11), facecolor="#f5f3f1")
    gs = fig.add_gridspec(13, 6, left=0.05, right=0.97, top=0.965, bottom=0.05, hspace=0.62, wspace=0.55)

    sector_colors = {
        "Transportation and Storage": "#b23a48",
        "Total Households": "#d18b47",
        "Agriculture, Forestry and Fishing": "#7a5c3e",
    }

    for idx, sector in enumerate(focus_sectors):
        ax = fig.add_subplot(gs[:5, idx * 2 : (idx + 1) * 2])
        add_card(ax)
        values = annual.loc[sector, comparison_years]
        years = [int(year) for year in comparison_years]
        ymin = values.min() * 0.97
        ymax = values.max() * 1.03
        ax.plot(years, values.values, color=sector_colors[sector], linewidth=3)
        ax.scatter(years[-1], values.values[-1], color=sector_colors[sector], s=42, zorder=4)
        ax.set_xlim(2015, 2023)
        ax.set_ylim(ymin, ymax)
        ax.set_xticks([2015, 2019, 2023])
        ax.grid(axis="y", color="#ece3dd")
        ax.set_title(sector, loc="left", fontsize=12.5, pad=12)
        if idx == 0:
            ax.set_ylabel("Metric tons of CO2 equivalent")
        else:
            ax.set_yticklabels([])
        change = (annual.loc[sector, "2023"] - annual.loc[sector, "2015"]) / annual.loc[sector, "2015"] * 100
        ax.text(
            0.98,
            0.08,
            f"{change:+.1f}% since 2015",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=10,
            color="#5c3d2c",
            bbox={"boxstyle": "round,pad=0.28", "fc": "#fbf2ed", "ec": "#e1c4b2"},
        )

    title_ax = fig.add_subplot(gs[5:6, :])
    title_ax.axis("off")
    title_ax.text(
        0.0,
        0.48,
        "Focusing on 2015-2023 highlights that transportation, households, and agriculture saw little sustained decline.",
        fontsize=14.5,
        weight="bold",
        color="#4a2f27",
    )
    title_ax.text(
        0.0,
        0.03,
        "This narrowed window isolates the post-Paris Agreement period, when a reader might expect clearer progress.",
        fontsize=10.5,
        color="#6c554b",
    )

    ax4 = fig.add_subplot(gs[7:, :])
    add_card(ax4)
    add_chart_header(
        ax4,
        "Most of the net decline came from electricity, not broad-based cuts across the economy",
        "Absolute change in annual greenhouse-gas emissions by sector, 2010 to 2023.",
    )
    sector_changes = annual.drop(index="Total Industries + Total Households")
    sector_changes = sector_changes.assign(change=sector_changes["2023"] - sector_changes["2010"]).sort_values("change")
    reduction_total = annual.loc["Total Industries + Total Households", "2010"] - annual.loc["Total Industries + Total Households", "2023"]
    electricity_share = abs(sector_changes.loc["Electricity, gas, steam and air conditioning supply", "change"]) / reduction_total * 100

    colors = ["#355f8c" if value < 0 else "#bb5a4d" for value in sector_changes["change"]]
    ax4.barh(sector_changes.index, sector_changes["change"], color=colors, edgecolor="none", height=0.62)
    ax4.axvline(0, color="#947f76", linewidth=1)
    ax4.grid(axis="x", color="#ece3dd")
    ax4.set_axisbelow(True)
    ax4.set_xlabel("Change in metric tons of CO2 equivalent")
    xlim = max(abs(sector_changes["change"].min()), abs(sector_changes["change"].max()))
    ax4.set_xlim(-xlim * 1.25, xlim * 1.15)

    for y, value in enumerate(sector_changes["change"]):
        text = f"{value / 1000:+.2f}B"
        if value < 0:
            ax4.text(value - 55, y, text, va="center", ha="right", fontsize=10)
        else:
            ax4.text(value + 55, y, text, va="center", ha="left", fontsize=10)

    ax4.text(
        0.98,
        0.06,
        f"Electricity accounts for about {electricity_share:.0f}% of the total reduction,\nwhile transport, agriculture, and construction all rise.",
        transform=ax4.transAxes,
        ha="right",
        va="bottom",
        fontsize=10,
        color="#5c3d2c",
        bbox={"boxstyle": "round,pad=0.35", "fc": "#fbf2ed", "ec": "#e1c4b2"},
    )

    save_page_as_png(fig, "checkpoint_page_2_false.png")
    return fig


def make_writeup_page(annual):
    total_2010 = annual.loc["Total Industries + Total Households", "2010"]
    total_2023 = annual.loc["Total Industries + Total Households", "2023"]
    total_change = (total_2023 - total_2010) / total_2010 * 100
    electricity_change = (
        (annual.loc["Electricity, gas, steam and air conditioning supply", "2023"]
         - annual.loc["Electricity, gas, steam and air conditioning supply", "2010"])
        / annual.loc["Electricity, gas, steam and air conditioning supply", "2010"]
        * 100
    )
    transport_change = (
        (annual.loc["Transportation and Storage", "2023"] - annual.loc["Transportation and Storage", "2010"])
        / annual.loc["Transportation and Storage", "2010"]
        * 100
    )

    fig = plt.figure(figsize=(8.5, 11), facecolor="#fbfaf8")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    fig.text(0.055, 0.944, "Proposition and techniques", fontsize=22, weight="bold", color="#402a1f")

    info_lines = [
        "Group members: [Add full names and UCSD emails here before submitting]",
        f"Dataset used: {DATASET_PATH.name}",
        f"Proposition: {PROPOSITION}",
        f"Which side we currently lean toward: {LEANING}",
    ]
    y = 0.87
    for line in info_lines:
        fig.text(0.06, y, line, fontsize=11.3, color="#45342b")
        y -= 0.035

    sections = [
        (
            "Page 1 techniques used to persuade that the proposition is true",
            [
                f"The first chart uses the full 2010-2023 span and a clean zero-baseline area fill, which makes the overall decline from {format_mtco2(total_2010)} to {format_mtco2(total_2023)} feel steady and substantial ({total_change:+.1f}%).",
                "The title foregrounds the total percentage decrease before the reader sees any sector-level caveats, nudging attention toward the headline trend rather than exceptions.",
                f"The second chart sorts sectors by percentage change, which visually clusters declines together and highlights the sharp electricity-sector drop ({electricity_change:+.1f}%) as proof that decarbonization is working.",
                "We keep the full 2010-2023 period here because the proposition itself asks whether progress has happened since 2010, so the strongest fair case for the pro side uses the entire window.",
                "Sectors that increased are still shown, but they are visually de-emphasized in gray so they read more like minor caveats than central counterevidence.",
            ],
        ),
        (
            "Page 2 techniques used to persuade that the proposition is false",
            [
                "We intentionally narrow the time window to 2015-2023 to isolate the post-Paris Agreement years, when a skeptical reader might ask whether advanced economies delivered visible progress after major climate commitments.",
                "We cherry-pick transportation, households, and agriculture because they either rise or stay relatively flat over that period, making them strong counterexamples to the broad overall decline.",
                "The small multiples also use tight y-axis ranges, making recent movement feel flatter and more alarming than it would on a full zero-based scale.",
                f"Transportation is framed as a failure case because it ends above its 2010 level ({transport_change:+.1f}%), which undermines the idea of broad-based progress.",
                "The contribution chart reframes the story away from the total and toward where the cuts came from, suggesting the headline decline is overly dependent on one sector.",
                "Warm reds and browns create a more cautionary emotional tone than the cooler greens and blues on the first page, reinforcing skepticism before the reader finishes reading.",
            ],
        ),
        (
            "Current takeaway",
            [
                "At this checkpoint stage, the 'true' page feels more defensible overall because the total decline is real and not fabricated, but the 'false' page is strong because it reveals how much the story depends on framing and sector selection.",
                "Both pages use the same data truthfully in some places and strategically in others, which is exactly what makes persuasive visualization ethically slippery.",
            ],
        ),
    ]

    y = 0.705
    for title, bullets in sections:
        fig.text(0.06, y, title, fontsize=13.5, weight="bold", color="#402a1f")
        y -= 0.03
        for bullet in bullets:
            fig.text(0.075, y, f"• {bullet}", fontsize=10.7, color="#4a3b33", wrap=True)
            y -= 0.06
        y -= 0.012

    save_page_as_png(fig, "checkpoint_page_3_writeup.png")
    return fig


def main():
    apply_common_style()
    annual, _ = load_annual_series()

    figs = [
        make_true_page(annual),
        make_false_page(annual),
        make_writeup_page(annual),
    ]

    with PdfPages(OUTPUT_PDF) as pdf:
        for fig in figs:
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"Created {OUTPUT_PDF.name}")


if __name__ == "__main__":
    main()

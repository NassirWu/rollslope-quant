from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt  # noqa: E402
import pytest
from matplotlib.figure import Figure

from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes
from rollslope_quant.interfaces.visualization import slope_visualizer
from rollslope_quant.interfaces.visualization.slope_visualizer import (
    plot_from_dataframe,
    plot_slope_fitting,
)


@pytest.fixture
def market_df():
    return generate_v_reversal_market_data(seed=7, n_each=30)


@pytest.fixture
def xy_and_slope_result(market_df):
    x = market_df.index.to_numpy(dtype=float)
    y = market_df["close"].to_numpy(dtype=float)
    result = calculate_dynamic_slopes(x, y)
    return x, y, result


def _vline_x_values(ax) -> list[float]:
    return [
        line.get_xdata()[0]
        for line in ax.lines
        if len(line.get_xdata()) == 2 and line.get_xdata()[0] == line.get_xdata()[1]
    ]


def test_plot_slope_fitting_returns_figure(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    fig = plot_slope_fitting(x, y, result, show=False)

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_contains_raw_data_points(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    fig = plot_slope_fitting(x, y, result, show=False)
    ax = fig.axes[0]

    assert len(ax.collections) >= 1
    assert len(ax.collections[0].get_offsets()) == len(x)
    plt.close(fig)


def test_plot_contains_fitted_segment_lines(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    fig = plot_slope_fitting(x, y, result, show=False)
    ax = fig.axes[0]
    labels = ax.get_legend_handles_labels()[1]

    assert any(label.startswith("Segment A") for label in labels)
    assert any(label.startswith("Segment B") for label in labels)
    assert any(label.startswith("Segment C") for label in labels)
    plt.close(fig)


def test_plot_contains_two_breakpoint_vlines(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    fig = plot_slope_fitting(x, y, result, show=False)
    ax = fig.axes[0]
    labels = ax.get_legend_handles_labels()[1]

    vline_x_values = sorted(_vline_x_values(ax))
    assert len(vline_x_values) == 2
    assert vline_x_values == pytest.approx(sorted(result.breakpoints))
    assert "Breakpoint 1" in labels
    assert "Breakpoint 2" in labels
    plt.close(fig)


def test_title_contains_slope_and_r_squared_values(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    fig = plot_slope_fitting(x, y, result, show=False)
    ax = fig.axes[0]
    title = ax.get_title()

    assert "t1" in title
    assert "t2" in title
    assert "t3" in title
    assert "R-squared" in title
    plt.close(fig)


def test_mismatched_lengths_raise_value_error(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result

    with pytest.raises(ValueError):
        plot_slope_fitting(x[:-1], y, result, show=False)


def test_wrong_breakpoint_count_raises_value_error(xy_and_slope_result) -> None:
    import dataclasses

    x, y, result = xy_and_slope_result
    bad_result = dataclasses.replace(result, breakpoints=(result.breakpoints[0],))

    with pytest.raises(ValueError):
        plot_slope_fitting(x, y, bad_result, show=False)


def test_plot_from_dataframe_uses_close_column(market_df) -> None:
    fig = plot_from_dataframe(market_df, show=False)

    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_from_dataframe_with_explicit_slope_result_skips_recalculation(
    market_df, xy_and_slope_result, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, _, result = xy_and_slope_result
    called = False

    def fail_if_called(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal called
        called = True
        raise AssertionError("calculate_dynamic_slopes should not be called when slope_result is given")

    monkeypatch.setattr(slope_visualizer, "calculate_dynamic_slopes", fail_if_called)

    fig = plot_from_dataframe(market_df, slope_result=result, show=False)

    assert called is False
    assert isinstance(fig, Figure)
    plt.close(fig)


def test_plot_from_dataframe_missing_price_col_raises_clear_error(market_df) -> None:
    with pytest.raises(ValueError, match="missing_col"):
        plot_from_dataframe(market_df, price_col="missing_col", show=False)


def test_plot_from_dataframe_missing_x_col_raises_clear_error(market_df) -> None:
    with pytest.raises(ValueError, match="missing_x"):
        plot_from_dataframe(market_df, x_col="missing_x", show=False)


def test_save_path_writes_image_file(xy_and_slope_result, tmp_path: Path) -> None:
    x, y, result = xy_and_slope_result
    save_path = tmp_path / "slope_fit.png"

    fig = plot_slope_fitting(x, y, result, show=False, save_path=str(save_path))

    assert save_path.exists()
    assert save_path.stat().st_size > 0
    plt.close(fig)


def test_show_false_does_not_call_pyplot_show(
    xy_and_slope_result, monkeypatch: pytest.MonkeyPatch
) -> None:
    x, y, result = xy_and_slope_result
    show_called = False

    def fake_show(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal show_called
        show_called = True

    monkeypatch.setattr(plt, "show", fake_show)

    fig = plot_slope_fitting(x, y, result, show=False)

    assert show_called is False
    plt.close(fig)


def test_show_true_calls_pyplot_show(
    xy_and_slope_result, monkeypatch: pytest.MonkeyPatch
) -> None:
    x, y, result = xy_and_slope_result
    show_called = False

    def fake_show(*args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal show_called
        show_called = True

    monkeypatch.setattr(plt, "show", fake_show)

    fig = plot_slope_fitting(x, y, result, show=True)

    assert show_called is True
    plt.close(fig)


def test_ax_parameter_draws_on_existing_axes(xy_and_slope_result) -> None:
    x, y, result = xy_and_slope_result
    existing_fig, existing_ax = plt.subplots()

    returned_fig = plot_slope_fitting(x, y, result, show=False, ax=existing_ax)

    assert returned_fig is existing_fig
    plt.close(existing_fig)

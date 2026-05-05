import reflex as rx
from ..states.fitcheck_state import FitCheckState

CARD_BASE = {
    "background_color": "#0d1829",
    "border_radius": "10px",
    "padding": "16px",
    "border": "1px solid #1e293b",
    "width": "100%",
}


def _score_border_color() -> rx.Var:
    return rx.cond(
        FitCheckState.fit_score >= 7,
        "1px solid #22c55e",
        rx.cond(FitCheckState.fit_score >= 4, "1px solid #f59e0b", "1px solid #ef4444"),
    )


def _score_shadow() -> rx.Var:
    return rx.cond(
        FitCheckState.fit_score >= 7,
        "0 0 24px rgba(34, 197, 94, 0.2)",
        rx.cond(
            FitCheckState.fit_score >= 4,
            "0 0 24px rgba(245, 158, 11, 0.2)",
            "0 0 24px rgba(239, 68, 68, 0.2)",
        ),
    )


def _score_hex() -> rx.Var:
    return rx.cond(
        FitCheckState.fit_score >= 7,
        "#22c55e",
        rx.cond(FitCheckState.fit_score >= 4, "#f59e0b", "#ef4444"),
    )


def score_display() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text(
                "FIT SCORE",
                color="#475569",
                font_size="11px",
                font_weight="700",
                letter_spacing="0.1em",
            ),
            rx.hstack(
                rx.text(
                    FitCheckState.fit_score,
                    font_size="64px",
                    font_weight="800",
                    color=_score_hex(),
                    line_height="1",
                ),
                rx.vstack(
                    rx.text("out of", color="#334155", font_size="12px"),
                    rx.text("10", color="#475569", font_size="24px", font_weight="700"),
                    spacing="0",
                    align="start",
                    padding_bottom="6px",
                    align_self="flex-end",
                ),
                spacing="3",
                align="end",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            **CARD_BASE,
            "border": _score_border_color(),
            "box_shadow": _score_shadow(),
        },
    )


def strength_bullet(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="7px",
            height="7px",
            border_radius="50%",
            background_color="#22c55e",
            flex_shrink="0",
            margin_top="7px",
        ),
        rx.text(text, color="#e2e8f0", font_size="14px", line_height="1.6"),
        spacing="3",
        align="start",
        width="100%",
    )


def gap_bullet(text: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="7px",
            height="7px",
            border_radius="50%",
            background_color="#f59e0b",
            flex_shrink="0",
            margin_top="7px",
        ),
        rx.text(text, color="#e2e8f0", font_size="14px", line_height="1.6"),
        spacing="3",
        align="start",
        width="100%",
    )


def strengths_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("trending_up", size=15, color="#22c55e"),
                rx.text(
                    "Your Strengths",
                    color="#22c55e",
                    font_size="11px",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                ),
                spacing="2",
                align="center",
            ),
            rx.vstack(
                rx.foreach(FitCheckState.strengths, strength_bullet),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            **CARD_BASE,
            "border_left": "3px solid #22c55e",
        },
    )


def gaps_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("triangle_alert", size=15, color="#f59e0b"),
                rx.text(
                    "Gaps to Address",
                    color="#f59e0b",
                    font_size="11px",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                ),
                spacing="2",
                align="center",
            ),
            rx.vstack(
                rx.foreach(FitCheckState.gaps, gap_bullet),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            **CARD_BASE,
            "border_left": "3px solid #f59e0b",
        },
    )


def recommendation_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("lightbulb", size=15, color="#3b82f6"),
                rx.text(
                    "Recommendation",
                    color="#3b82f6",
                    font_size="11px",
                    font_weight="700",
                    text_transform="uppercase",
                    letter_spacing="0.1em",
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                FitCheckState.recommendation,
                color="#e2e8f0",
                font_size="14px",
                line_height="1.7",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={
            **CARD_BASE,
            "border_left": "3px solid #3b82f6",
        },
    )


def reset_button() -> rx.Component:
    return rx.button(
        "Analyze Another Role",
        on_click=FitCheckState.reset_analysis,
        width="100%",
        height="44px",
        background_color="transparent",
        border="1px solid white",
        border_radius="10px",
        color="white",
        cursor="pointer",
        font_size="14px",
        font_weight="500",
        _hover={"background_color": "rgba(255,255,255,0.05)", "border_color": "#3b82f6", "color": "#3b82f6"},
        transition="all 0.2s ease",
    )


def results_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("circle_check", size=22, color="#22c55e"),
            rx.text(
                "Analysis Complete",
                color="white",
                font_size="20px",
                font_weight="700",
            ),
            spacing="2",
            align="center",
        ),
        score_display(),
        strengths_card(),
        gaps_card(),
        recommendation_card(),
        reset_button(),
        spacing="4",
        width="100%",
        align="start",
        style={"animation": "fadeIn 0.4s ease-out"},
    )


def placeholder_state() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.icon("chart_bar", color="#1e293b", size=72),
            style={"animation": "pulse 2.5s ease-in-out infinite"},
        ),
        rx.text(
            "Your analysis will appear here",
            color="#334155",
            font_size="18px",
            font_weight="600",
            text_align="center",
        ),
        rx.text(
            "Paste a job description and resume to get started",
            color="#1e293b",
            font_size="13px",
            text_align="center",
        ),
        spacing="3",
        align="center",
        justify="center",
        padding_top="80px",
        padding_bottom="40px",
        width="100%",
    )


def results_panel() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.cond(
                FitCheckState.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("triangle_alert", color="#f87171", size=16),
                        rx.text(
                            FitCheckState.error_message,
                            color="#f87171",
                            font_size="14px",
                        ),
                        spacing="2",
                        align="start",
                    ),
                    background_color="#1e1a1a",
                    border="1px solid #7f1d1d",
                    border_radius="8px",
                    padding="12px",
                    width="100%",
                ),
                rx.fragment(),
            ),
            rx.cond(
                FitCheckState.show_results,
                results_content(),
                rx.cond(
                    FitCheckState.error_message == "",
                    placeholder_state(),
                    rx.fragment(),
                ),
            ),
            spacing="4",
            width="100%",
            align="start",
        ),
        style={
            "background_image": "linear-gradient(160deg, #0f172a 0%, #131f35 100%)",
            "padding": "24px",
            "border_radius": "14px",
            "border": "1px solid #1e293b",
            "width": "100%",
            "flex": "1",
            "min_height": "400px",
        },
    )

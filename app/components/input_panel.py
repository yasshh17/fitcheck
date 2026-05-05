import reflex as rx
from ..states.fitcheck_state import FitCheckState

TEXTAREA_STYLE = {
    "background_color": "#0d1829",
    "color": "white",
    "border": "1px solid #1e293b",
    "border_radius": "8px",
    "padding": "12px",
    "width": "100%",
    "font_size": "14px",
    "line_height": "1.6",
    "resize": "vertical",
    "min_height": "160px",
    "_placeholder": {"color": "#475569"},
    "_focus": {
        "outline": "none",
        "border_color": "#3b82f6",
        "box_shadow": "0 0 0 3px rgba(59, 130, 246, 0.15)",
    },
}

LABEL_STYLE = {
    "color": "#64748b",
    "font_size": "12px",
    "font_weight": "600",
    "text_transform": "uppercase",
    "letter_spacing": "0.08em",
}


def char_counter(count: int) -> rx.Component:
    return rx.text(
        count,
        " / 15,000 characters",
        color="#1e3a5f",
        font_size="11px",
        text_align="right",
        width="100%",
    )


def section_divider() -> rx.Component:
    return rx.box(height="1px", background_color="#0f172a", width="100%", margin_y="4px")


def analyze_button() -> rx.Component:
    return rx.button(
        rx.cond(
            FitCheckState.is_loading,
            rx.hstack(
                rx.spinner(size="2", color="white"),
                rx.text("Analyzing...", color="white", font_weight="700", font_size="15px"),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.icon("zap", size=16, color="white"),
                rx.text("Analyze Fit", color="white", font_weight="700", font_size="15px"),
                spacing="2",
                align="center",
            ),
        ),
        on_click=FitCheckState.analyze_fit,
        disabled=FitCheckState.is_loading,
        width="100%",
        height="48px",
        style={
            "background_image": rx.cond(
                FitCheckState.is_loading,
                "linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%)",
                "linear-gradient(90deg, #2563eb 0%, #3b82f6 100%)",
            ),
            "border_radius": "10px",
            "cursor": rx.cond(FitCheckState.is_loading, "not-allowed", "pointer"),
            "border": "none",
            "transition": "all 0.2s ease",
            "_hover": {
                "background_image": "linear-gradient(90deg, #1d4ed8 0%, #2563eb 100%)",
            },
        },
    )


def input_panel() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.vstack(
                rx.text("Job Description", style=LABEL_STYLE),
                rx.text_area(
                    placeholder="Paste the full job description here...",
                    value=FitCheckState.job_description,
                    on_change=FitCheckState.set_job_description,
                    rows="10",
                    max_length=15000,
                    style=TEXTAREA_STYLE,
                ),
                char_counter(FitCheckState.job_char_count),
                spacing="2",
                width="100%",
            ),
            section_divider(),
            rx.vstack(
                rx.text("Resume / Candidate Background", style=LABEL_STYLE),
                rx.text_area(
                    placeholder="Paste your resume or background summary here...",
                    value=FitCheckState.resume_text,
                    on_change=FitCheckState.set_resume_text,
                    rows="10",
                    max_length=15000,
                    style=TEXTAREA_STYLE,
                ),
                char_counter(FitCheckState.resume_char_count),
                spacing="2",
                width="100%",
            ),
            analyze_button(),
            spacing="5",
            width="100%",
            align="start",
        ),
        style={
            "background_image": "linear-gradient(160deg, #0f172a 0%, #131f35 100%)",
            "padding": "24px",
            "border_radius": "14px",
            "border": "1px solid #1e293b",
            "border_left": "3px solid #3b82f6",
            "width": "100%",
            "flex": "1",
        },
    )

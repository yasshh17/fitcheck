# FitCheck: AI-powered resume analyzer. Users paste a job description and resume,
# then receive a fit score (1-10), strengths, gaps, and a hiring recommendation via OpenAI.

import reflex as rx
from .components.input_panel import input_panel
from .components.results_panel import results_panel

_KEYFRAMES = """
<style>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0);    }
}
</style>
"""


def navbar() -> rx.Component:
    return rx.box(
        rx.box(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="50%",
                        background_color="#3b82f6",
                        box_shadow="0 0 10px rgba(59,130,246,0.7)",
                    ),
                    rx.text(
                        "FitCheck",
                        color="white",
                        font_size="20px",
                        font_weight="700",
                        letter_spacing="0.02em",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.text(
                    "AI Resume Analyzer",
                    color="#475569",
                    font_size="13px",
                    font_weight="500",
                    letter_spacing="0.04em",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            max_width="1200px",
            margin="0 auto",
            padding=rx.breakpoints(initial="0 16px", md="0 32px"),
        ),
        background_color="#0a0f1e",
        border_bottom="1px solid #0f172a",
        padding_y="16px",
        width="100%",
    )


def index() -> rx.Component:
    return rx.box(
        rx.html(_KEYFRAMES),
        rx.box(height="4px", background_color="#3b82f6", width="100%"),
        navbar(),
        rx.box(
            rx.flex(
                input_panel(),
                results_panel(),
                direction=rx.breakpoints(initial="column", md="row"),
                gap="6",
                width="100%",
                align="start",
            ),
            max_width="1200px",
            margin="0 auto",
            width="100%",
            padding=rx.breakpoints(initial="24px 16px", md="32px 32px"),
        ),
        background_color="#0a0f1e",
        min_height="100vh",
    )


app = rx.App(
    style={
        "background_color": "#0a0f1e",
        "color": "white",
        "font_family": "Inter, system-ui, sans-serif",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
    ],
)
app.add_page(index, route="/", title="FitCheck — AI Resume Analyzer")

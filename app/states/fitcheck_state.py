import os
import sys
import time
import json
from pathlib import Path
import reflex as rx
import openai
from dotenv import load_dotenv

# Load .env from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


SYSTEM_PROMPT = (
    "You are a senior technical recruiter evaluating candidate fit for a software "
    "engineering role. Your output must be strictly valid JSON with no extra text, "
    "markdown, or code fences."
)

MAX_INPUT_CHARS = 15_000
RATE_LIMIT_SECONDS = 5
DAILY_REQUEST_CAP = 50


class FitCheckState(rx.State):
    job_description: str = ""
    resume_text: str = ""
    is_loading: bool = False
    show_results: bool = False
    fit_score: int = 0
    strengths: list[str] = []
    gaps: list[str] = []
    recommendation: str = ""
    error_message: str = ""

    # Private rate-limiting vars (underscore prefix = not synced to frontend)
    _last_analysis_time: float = 0.0
    _daily_request_count: int = 0
    _last_request_day: int = 0

    def set_job_description(self, value: str):
        self.job_description = value

    def set_resume_text(self, value: str):
        self.resume_text = value

    @rx.var
    def can_analyze(self) -> bool:
        return bool(self.job_description.strip()) and bool(self.resume_text.strip())

    @rx.var
    def score_color(self) -> str:
        if self.fit_score >= 7:
            return "green"
        elif self.fit_score >= 4:
            return "orange"
        return "red"

    @rx.var
    def job_char_count(self) -> int:
        return len(self.job_description)

    @rx.var
    def resume_char_count(self) -> int:
        return len(self.resume_text)

    async def analyze_fit(self):
        self.error_message = ""
        self.show_results = False

        # Input presence check
        if not self.job_description.strip() or not self.resume_text.strip():
            self.error_message = "Please provide both a job description and a resume."
            return

        # Input length check — server-side guard mirrors textarea max_length
        if len(self.job_description) > MAX_INPUT_CHARS or len(self.resume_text) > MAX_INPUT_CHARS:
            self.error_message = f"Input too long. Maximum {MAX_INPUT_CHARS:,} characters per field."
            return

        # Rate limiting — per-session cooldown + daily cap
        now = time.time()
        today = int(now // 86400)
        if today != self._last_request_day:
            self._daily_request_count = 0
            self._last_request_day = today
        if now - self._last_analysis_time < RATE_LIMIT_SECONDS:
            self.error_message = "Please wait a moment before analyzing again."
            return
        if self._daily_request_count >= DAILY_REQUEST_CAP:
            self.error_message = "Daily analysis limit reached. Please try again tomorrow."
            return

        # API key check — .get() avoids KeyError leaking var name to the UI
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            self.error_message = "Service configuration error. Please contact the administrator."
            print("[FitCheck] OPENAI_API_KEY is not set", file=sys.stderr)
            return

        self.is_loading = True
        self._last_analysis_time = now
        self._daily_request_count += 1
        yield

        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            user_message = (
                f"Job Description:\n{self.job_description}\n\n"
                f"Candidate Resume / Background:\n{self.resume_text}\n\n"
                'Return JSON with keys: "fit_score" (int 1-10), "strengths" (list of 3 strings), '
                '"gaps" (list of 2-3 strings), "recommendation" (1-2 sentence string).'
            )
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                timeout=30.0,
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)

            # Schema validation before accepting values
            required_keys = ("fit_score", "strengths", "gaps", "recommendation")
            if not all(k in data for k in required_keys):
                raise ValueError(f"Missing keys in AI response: {list(data.keys())}")

            self.fit_score = max(1, min(10, int(data["fit_score"])))
            self.strengths = list(data["strengths"])[:5]
            self.gaps = list(data["gaps"])[:5]
            self.recommendation = str(data["recommendation"])[:1000]
            self.show_results = True

        except openai.APITimeoutError:
            self.error_message = "Request timed out. Please try again."
            print("[FitCheck] OpenAI API timeout", file=sys.stderr)

        except openai.AuthenticationError:
            self.error_message = "Service authentication error. Please contact the administrator."
            print("[FitCheck] OpenAI authentication error — check OPENAI_API_KEY", file=sys.stderr)

        except openai.RateLimitError:
            self.error_message = "Service is temporarily busy. Please try again in a moment."
            print("[FitCheck] OpenAI rate limit hit", file=sys.stderr)

        except openai.APIConnectionError:
            self.error_message = "Could not reach the AI service. Check your internet connection."
            print("[FitCheck] OpenAI connection error", file=sys.stderr)

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.error_message = "Could not parse the AI response. Please try again."
            print(f"[FitCheck] Parse/validation error: {e}", file=sys.stderr)

        except Exception as e:
            self.error_message = "An unexpected error occurred. Please try again."
            print(f"[FitCheck] Unexpected error: {type(e).__name__}: {e}", file=sys.stderr)

        self.is_loading = False

    def reset_analysis(self):
        self.job_description = ""
        self.resume_text = ""
        self.is_loading = False
        self.show_results = False
        self.fit_score = 0
        self.strengths = []
        self.gaps = []
        self.recommendation = ""
        self.error_message = ""

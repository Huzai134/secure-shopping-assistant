# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo
from functools import cached_property

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import Client
from google.genai import types
from app.tools import redeem_discount_code, award_loyalty_points

import os
import google.auth

try:
    _, project_id = google.auth.default()
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
except Exception:
    os.environ["GOOGLE_CLOUD_PROJECT"] = "mock-project"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


class CustomGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        # Load API key securely from environment variables
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        return Client(api_key=api_key)


root_agent = Agent(
    name="shopping_assistant",
    model=CustomGemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="You are an AI shopping assistant for a retail store. Help customers find items, answer queries, redeem single-use discount codes using the redeem_discount_code tool, and award loyalty points after a successful purchase using the award_loyalty_points tool. Always ask for their registered user ID if not provided.",
    tools=[redeem_discount_code, award_loyalty_points],
)

app = App(
    root_agent=root_agent,
    name="app",
)

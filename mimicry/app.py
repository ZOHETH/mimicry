import os
from typing import Optional

from flask import Flask

from agent import Agent


def create_app(
        agent: Optional["Agent"] = None,
) -> Flask:
    app = Flask(__name__)
    app.agent = agent

    return app

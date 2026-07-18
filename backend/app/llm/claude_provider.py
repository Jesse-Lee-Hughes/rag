import asyncio
import json
import os
import shutil
from typing import List, Optional

from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    """Claude implementation that shells out to the Claude Code CLI (`claude -p`).

    This provider requires no API key: it uses the Claude subscription that the
    local `claude` CLI is already authenticated with. Useful when you have a
    Claude subscription but no API token bucket.

    Configuration (all optional, via environment):
        CLAUDE_BIN:     path/name of the CLI binary (default "claude")
        CLAUDE_MODEL:   model alias to pass to `--model` (default: CLI default)
        CLAUDE_TIMEOUT: per-call timeout in seconds (default 120)
    """

    def __init__(self, model: Optional[str] = None):
        self.bin = os.getenv("CLAUDE_BIN", "claude")
        self.model = model or os.getenv("CLAUDE_MODEL") or None
        self.timeout = float(os.getenv("CLAUDE_TIMEOUT", "120"))

        # Fail fast if the CLI isn't on PATH so the factory can fall back.
        if shutil.which(self.bin) is None:
            raise ValueError(
                f"Claude CLI '{self.bin}' not found on PATH. Install it "
                "(`npm i -g @anthropic-ai/claude-code`) and authenticate, "
                "or set CLAUDE_BIN."
            )

    async def _run(self, prompt: str, system_prompt: Optional[str] = None) -> dict:
        """Run `claude -p` once and return the parsed JSON result object."""
        args = [self.bin, "-p", prompt, "--output-format", "json"]
        if system_prompt:
            args += ["--append-system-prompt", system_prompt]
        if self.model:
            args += ["--model", self.model]

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=self.timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise Exception(f"Claude CLI timed out after {self.timeout}s")

        if proc.returncode != 0:
            raise Exception(
                f"Claude CLI exited {proc.returncode}: {stderr.decode(errors='replace').strip()}"
            )

        try:
            payload = json.loads(stdout.decode(errors="replace"))
        except json.JSONDecodeError as e:
            raise Exception(f"Could not parse Claude CLI output: {e}")

        if payload.get("is_error"):
            raise Exception(f"Claude CLI reported an error: {payload.get('result')}")

        return payload

    async def generate_response(
        self,
        query: str,
        context: List[str],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Generate a response with `claude -p`.

        `temperature` and `max_tokens` are accepted for interface compatibility
        but are not exposed by the CLI, so they are ignored here.
        """
        context_text = "\n\n".join(context)
        prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

        payload = await self._run(prompt, system_prompt=system_prompt)
        return payload.get("result", "")

    async def health_check(self) -> bool:
        """Check the CLI is present and can produce a completion."""
        try:
            payload = await self._run("Reply with the single word: ok")
            return bool(payload.get("result"))
        except Exception:
            return False

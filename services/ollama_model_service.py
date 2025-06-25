import aiohttp
import json
from typing import List, Optional

from models.settings import Settings
from utils.log_util import get_logger

logger = get_logger("OllamaPatternService")


class OllamaPathPatternService:
    def __init__(self, settings_: Settings):
        self.model = settings_.ollama_model
        self.url = f"{settings_.ollama_host}/api/generate"
        self.prompt_prefix = (
            "You are an assistant that analyzes a list of URL paths from a single domain.\n\n"
            "Your task is to extract the most meaningful and generalized path patterns that refer to developer documentation.\n"
            "This includes paths about APIs, SDKs, guides, integration docs, tutorials, and reference materials.\n\n"
            "Instructions:\n"
            "- Group similar paths using wildcards (e.g., /docs/*, /sdk/python/*) if they share structure.\n"
            "- Exclude irrelevant paths such as login, contact, blog, marketing, or social media.\n"
            "- Never return root-level '/' or empty string as a pattern.\n"
            "- Discard fragment identifiers (e.g., #section) and query parameters.\n"
            "- Remove duplicates and overlapping patterns; keep only the most general and representative ones.\n"
            "- Output must be sorted by relevance and breadth of coverage.\n\n"
            "Respond ONLY with a valid JSON object where each value is a general path pattern, like:\n"
            "{\n  \"1\": \"/docs/*\",\n  \"2\": \"/docs/api/*\" \n}\n\n"
            "Do NOT include any explanations or full URLs. Return only the JSON output.\n\n"
            "Input paths:\n"
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            logger.debug("🔌 ClientSession initialized.")

    async def shutdown(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.debug("🔒 ClientSession closed.")

    def _build_prompt(self, paths: List[str]) -> str:
        return self.prompt_prefix + "\n".join(f"{i + 1}. {path}" for i, path in enumerate(paths))

    async def extract_path_patterns(self, paths: List[str]) -> List[str]:
        if not self.session:
            raise RuntimeError("ClientSession is not initialized. Call 'await start()' first.")

        prompt = self._build_prompt(paths)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False
        }

        try:
            async with self.session.post(self.url, json=payload) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Ollama HTTP {response.status}:\n{text}")

                data = await response.json()
                raw = data.get("response", "").strip()

                if raw.startswith("```json"):
                    raw = raw.removeprefix("```json").removesuffix("```").strip()

                logger.info("🧠 Received raw model response.")

                try:
                    parsed = json.loads(raw)
                    patterns = list(dict.fromkeys(parsed.values()))
                    logger.info(f"✅ Extracted {len(patterns)} path patterns.")
                    return patterns
                except json.JSONDecodeError as e:
                    logger.error("❌ Failed to parse model output as JSON.")
                    raise RuntimeError(f"Invalid JSON: {e}\nRaw response:\n{raw}")

        except Exception as e:
            logger.error(f"🔌 Ollama request failed: {e}")
            raise

    async def extract_patterns_from_batches(
        self,
        hrefs: List[str],
        batch_size: int = 10
    ) -> List[str]:
        await self.start()

        all_patterns = []
        total_batches = (len(hrefs) + batch_size - 1) // batch_size

        for i in range(total_batches):
            batch = hrefs[i * batch_size:(i + 1) * batch_size]
            logger.info(f"🔍 Processing batch {i + 1}/{total_batches} ({len(batch)} items)")

            try:
                patterns = await self.extract_path_patterns(batch)
                logger.info(f"✅ Batch {i + 1}: Extracted {len(patterns)} patterns.")
                all_patterns.extend(patterns)
            except Exception as e:
                logger.warning(f"❌ Batch {i + 1} failed: {e}")

        unique_patterns = list(dict.fromkeys(all_patterns))
        logger.info(f"📦 Total unique patterns extracted: {len(unique_patterns)}")
        return unique_patterns

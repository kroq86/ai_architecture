from typing import List


class Renderer:
    def render(self, text: str) -> List[str]:
        clean = text.strip() or "I could not produce a response."
        if len(clean) <= 4000:
            return [clean]
        return [clean[i : i + 4000] for i in range(0, len(clean), 4000)]

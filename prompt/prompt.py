from tkr_utils import logs_and_exceptions, setup_logging
from typing import List, Dict

# Set up the logger
logger = setup_logging(__file__)

class Prompt:
    @logs_and_exceptions(logger)
    def __init__(self):
        self.system_prompts: List[str] = []
        self.agent_prompts: List[str] = []
        self.task_prompts: List[str] = []

    @logs_and_exceptions(logger)
    def add_system_prompt(self, prompt: str) -> None:
        logger.info("Adding system prompt")
        self.system_prompts.append(prompt)

    @logs_and_exceptions(logger)
    def add_agent_prompt(self, prompt: str) -> None:
        logger.info("Adding agent prompt")
        self.agent_prompts.append(prompt)

    @logs_and_exceptions(logger)
    def add_task_prompt(self, prompt: str) -> None:
        logger.info("Adding task prompt")
        self.task_prompts.append(prompt)

    @logs_and_exceptions(logger)
    def get_full_prompt(self) -> List[Dict[str, str]]:
        logger.info("Combining prompts")
        combined_prompts = []
        for prompt in self.system_prompts:
            combined_prompts.append({"role": "system", "content": prompt})
        for prompt in self.agent_prompts:
            combined_prompts.append({"role": "user", "content": prompt})
        for prompt in self.task_prompts:
            combined_prompts.append({"role": "assistant", "content": prompt})
        return combined_prompts
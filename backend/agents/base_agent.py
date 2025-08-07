"""Base agent class for AI DevOps Agent Platform."""

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from loguru import logger

from config.settings import settings
from shared.models import AgentResult, CarbonEmission


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.model_name = ""
        
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Process the input and return a result."""
        pass
    
    def _calculate_carbon_emission(self, tokens_used: int, model_name: str) -> Optional[CarbonEmission]:
        """Calculate carbon emission for the operation."""
        if not settings.enable_carbon_tracking:
            return None
            
        # Rough estimates (grams CO2 per 1000 tokens)
        emission_factors = {
            "gpt-4": 0.5,
            "gpt-4-turbo": 0.4,
            "gpt-4-vision": 0.6,
            "claude-3": 0.3,
            "claude-3-sonnet": 0.25,
            "claude-3-haiku": 0.15
        }
        
        base_model = model_name.split("-")[0:2]  # e.g., "gpt-4" from "gpt-4-turbo-preview"
        base_key = "-".join(base_model)
        
        factor = emission_factors.get(base_key, 0.5)  # Default factor
        estimated_co2 = (tokens_used / 1000) * factor
        
        return CarbonEmission(
            task_id="",  # Will be set by caller
            agent_name=self.name,
            model_name=model_name,
            tokens_used=tokens_used,
            estimated_co2_grams=estimated_co2
        )
    
    async def execute(self, input_data: Dict[str, Any], task_id: str = "") -> AgentResult:
        """Execute the agent with timing and error handling."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting {self.name} agent processing")
            result = await self.process(input_data)
            result.execution_time = time.time() - start_time
            
            # Set task_id for carbon emission if available
            if result.carbon_emission:
                result.carbon_emission.task_id = task_id
                
            logger.info(f"{self.name} agent completed in {result.execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{self.name} agent failed after {execution_time:.2f}s: {str(e)}")
            
            return AgentResult(
                agent_name=self.name,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
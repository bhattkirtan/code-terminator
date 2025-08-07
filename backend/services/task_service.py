"""Task service for managing processing tasks."""

import asyncio
from datetime import datetime
from typing import Dict, Optional

from loguru import logger

from shared.models import ProcessingTask, ProcessingStatus


class TaskService:
    """Service for managing processing tasks."""
    
    def __init__(self):
        self._tasks: Dict[str, ProcessingTask] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(self, task: ProcessingTask) -> None:
        """Create a new task."""
        async with self._lock:
            self._tasks[task.task_id] = task
            logger.info(f"Created task {task.task_id}")
    
    async def get_task(self, task_id: str) -> Optional[ProcessingTask]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    async def update_task(
        self, 
        task_id: str, 
        status: Optional[ProcessingStatus] = None,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result: Optional[Dict] = None
    ) -> bool:
        """Update task status and information."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if status is not None:
                task.status = status
            if progress is not None:
                task.progress = progress
            if message is not None:
                task.message = message
            if error is not None:
                task.error = error
            if result is not None:
                task.result = result
            
            task.updated_at = datetime.utcnow()
            logger.info(f"Updated task {task_id}: {task.status} ({task.progress}%)")
            return True
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False
            
            if task.status in [ProcessingStatus.PENDING, ProcessingStatus.PROCESSING]:
                task.status = ProcessingStatus.FAILED
                task.error = "Task cancelled by user"
                task.updated_at = datetime.utcnow()
                logger.info(f"Cancelled task {task_id}")
                return True
            
            return False
    
    async def list_tasks(self, limit: int = 100) -> list[ProcessingTask]:
        """List recent tasks."""
        tasks = list(self._tasks.values())
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """Clean up old completed tasks."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        async with self._lock:
            to_remove = []
            for task_id, task in self._tasks.items():
                if (task.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED] and
                    task.updated_at.timestamp() < cutoff_time):
                    to_remove.append(task_id)
            
            for task_id in to_remove:
                del self._tasks[task_id]
            
            if to_remove:
                logger.info(f"Cleaned up {len(to_remove)} old tasks")
            
            return len(to_remove)
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.utcnow().isoformat()
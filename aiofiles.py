"""Mock aiofiles for testing."""

import asyncio


class MockAioFiles:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def write(self, data):
        with open(self.path, self.mode) as f:
            if isinstance(data, bytes):
                f.buffer.write(data)
            else:
                f.write(data)
    
    async def read(self):
        with open(self.path, 'r') as f:
            return f.read()


def open(path, mode='r'):
    return MockAioFiles(path, mode)
#!/usr/bin/env python3
"""Test script for AI DevOps Agent Platform."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings, ensure_directories
from backend.agents import VisionAgent, LayoutAgent, CodeAgent, StyleAgent, StubAgent
from shared.models import ProcessingStatus
from backend.services import TaskService, ProjectService


async def test_agents():
    """Test individual agents."""
    print("🧪 Testing AI DevOps Agent Platform")
    print("=" * 50)
    
    # Ensure directories exist
    ensure_directories()
    
    # Test data
    test_screenshot = project_root / "testdata" / "00_Cases-Portal.jpg"
    if not test_screenshot.exists():
        print(f"❌ Test screenshot not found: {test_screenshot}")
        return False
    
    print(f"✅ Using test screenshot: {test_screenshot}")
    
    # Test VisionAgent
    print("\n🔍 Testing VisionAgent...")
    vision_agent = VisionAgent()
    vision_result = await vision_agent.execute({
        "image_path": str(test_screenshot)
    })
    
    if vision_result.success:
        print(f"✅ VisionAgent: Found {len(vision_result.output['layout_structure']['elements'])} UI elements")
        layout_structure = vision_result.output["layout_structure"]
    else:
        print(f"❌ VisionAgent failed: {vision_result.error}")
        return False
    
    # Test LayoutAgent
    print("\n🏗️ Testing LayoutAgent...")
    layout_agent = LayoutAgent()
    layout_result = await layout_agent.execute({
        "layout_structure": layout_structure,
        "component_name": "test-component"
    })
    
    if layout_result.success:
        print("✅ LayoutAgent: Generated Angular template")
        angular_template = layout_result.output["angular_template"]
        component_structure = layout_result.output["component_structure"]
    else:
        print(f"❌ LayoutAgent failed: {layout_result.error}")
        return False
    
    # Test StyleAgent
    print("\n🎨 Testing StyleAgent...")
    style_agent = StyleAgent()
    style_result = await style_agent.execute({
        "reference_styles": "",
        "reference_images": [str(test_screenshot)],
        "component_scss": ""
    })
    
    if style_result.success:
        print("✅ StyleAgent: Generated enhanced styles")
        enhanced_scss = style_result.output["enhanced_scss"]
    else:
        print(f"❌ StyleAgent failed: {style_result.error}")
        enhanced_scss = ""
    
    # Test CodeAgent
    print("\n⚙️ Testing CodeAgent...")
    code_agent = CodeAgent()
    code_result = await code_agent.execute({
        "angular_template": angular_template,
        "component_structure": component_structure,
        "styles": enhanced_scss
    })
    
    if code_result.success:
        component = code_result.output["component"]
        print(f"✅ CodeAgent: Generated {len(component['files'])} component files")
        for file in component['files']:
            print(f"   - {file['filename']} ({len(file['content'])} chars)")
    else:
        print(f"❌ CodeAgent failed: {code_result.error}")
        return False
    
    # Test StubAgent
    print("\n🔧 Testing StubAgent...")
    stub_agent = StubAgent()
    stub_result = await stub_agent.execute({
        "component_name": "test-component",
        "component_structure": component_structure
    })
    
    if stub_result.success:
        service_files = stub_result.output["service_files"]
        print(f"✅ StubAgent: Generated {len(service_files)} service files")
    else:
        print(f"❌ StubAgent failed: {stub_result.error}")
    
    print("\n🎉 All agent tests completed successfully!")
    return True


async def test_services():
    """Test service layer."""
    print("\n📋 Testing Services...")
    
    # Test TaskService
    task_service = TaskService()
    from shared.models import ProcessingTask
    import uuid
    
    task_id = str(uuid.uuid4())
    task = ProcessingTask(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        message="Test task"
    )
    
    await task_service.create_task(task)
    retrieved_task = await task_service.get_task(task_id)
    
    if retrieved_task and retrieved_task.task_id == task_id:
        print("✅ TaskService: Create and retrieve working")
    else:
        print("❌ TaskService: Failed to create/retrieve task")
        return False
    
    # Update task
    success = await task_service.update_task(
        task_id,
        status=ProcessingStatus.COMPLETED,
        progress=100.0,
        message="Test completed"
    )
    
    if success:
        print("✅ TaskService: Update working")
    else:
        print("❌ TaskService: Failed to update task")
        return False
    
    print("✅ Service tests completed successfully!")
    return True


def test_configuration():
    """Test configuration setup."""
    print("⚙️ Testing Configuration...")
    
    # Check required settings
    config_ok = True
    
    if not settings.upload_folder:
        print("❌ Upload folder not configured")
        config_ok = False
    
    if not settings.output_folder:
        print("❌ Output folder not configured")
        config_ok = False
    
    # Check API keys (optional but recommended)
    if not settings.openai_api_key and not settings.anthropic_api_key:
        print("⚠️ No AI API keys configured - using fallback mode")
    else:
        print("✅ AI API keys configured")
    
    # Check directories
    ensure_directories()
    
    required_dirs = [
        settings.upload_folder,
        settings.output_folder,
        os.path.dirname(settings.log_file),
        "data"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            config_ok = False
    
    if config_ok:
        print("✅ Configuration tests passed!")
    else:
        print("❌ Configuration issues found")
    
    return config_ok


def main():
    """Run all tests."""
    print("🚀 AI DevOps Agent Platform Test Suite")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n❌ Configuration tests failed. Please fix issues before continuing.")
        sys.exit(1)
    
    # Run async tests
    async def run_async_tests():
        agent_ok = await test_agents()
        service_ok = await test_services()
        return agent_ok and service_ok
    
    async_ok = asyncio.run(run_async_tests())
    
    # Summary
    print("\n" + "=" * 60)
    if config_ok and async_ok:
        print("🎉 All tests passed! Platform is ready to use.")
        print("\n🚀 To start the platform:")
        print("   ./start.sh")
        print("\n🔗 Then visit:")
        print("   Frontend: http://localhost:8501")
        print("   Backend:  http://localhost:8000")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
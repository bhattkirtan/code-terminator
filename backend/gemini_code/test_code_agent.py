"""
Test client for Enhanced Code Agent API
Demonstrates how to use the enhanced API for project generation
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8001"


def test_prerequisites():
    """Test prerequisites check"""
    print("🔍 Checking system prerequisites...")
    try:
        response = requests.get(f"{API_BASE_URL}/prerequisites")
        if response.status_code == 200:
            data = response.json()
            print("✅ Prerequisites check completed")
            print(f"   All tools available: {data['all_available']}")
            for tool, available in data["tools"].items():
                status = "✅" if available else "❌"
                print(f"   {status} {tool}")

            if data["missing"]:
                print(f"   Missing tools: {', '.join(data['missing'])}")

            return data["all_available"]
        else:
            print(f"❌ Prerequisites check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Prerequisites check error: {e}")
        return False


def generate_project(
    project_name: str,
    context_path: str = None,
    auto_build: bool = True,
    auto_run: bool = False,
):
    """Generate a new Angular 20 project"""
    print(f"🚀 Generating project: {project_name}")

    project_data = {
        "project_name": project_name,
        "context_file_path": context_path,
        "auto_build": auto_build,
        "auto_run": auto_run,
        "fix_issues": True,
    }

    try:
        response = requests.post(f"{API_BASE_URL}/generate", json=project_data)

        if response.status_code == 200:
            result = response.json()
            print("✅ Project generation started")
            print(f"   Project ID: {result['project_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Project Path: {result['project_path']}")
            return result["project_id"]
        else:
            print(f"❌ Project generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Project generation error: {e}")
        return None


def check_project_status(project_id: str):
    """Check project generation status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status/{project_id}")
        if response.status_code == 200:
            status = response.json()
            return status
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None


def monitor_project_generation(project_id: str, max_wait_time: int = 600):
    """Monitor project generation progress"""
    print(f"📊 Monitoring project generation: {project_id}")

    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        status = check_project_status(project_id)

        if not status:
            break

        print(
            f"   Status: {status['status']} | Step: {status['current_step']} | Progress: {status['progress']}%"
        )

        if status["logs"]:
            for log in status["logs"][-3:]:  # Show last 3 logs
                print(f"   📝 {log}")

        if status["errors"]:
            for error in status["errors"]:
                print(f"   ❌ {error}")

        if status["status"] in ["completed", "failed"]:
            print(f"\n🎯 Final Status: {status['status']}")
            if status["status"] == "completed":
                print("✅ Project generation completed successfully!")
            else:
                print("❌ Project generation failed!")
            break

        time.sleep(5)  # Wait 5 seconds before next check

    return status


def list_projects():
    """List all generated projects"""
    print("📁 Listing all projects...")
    try:
        response = requests.get(f"{API_BASE_URL}/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data["projects"]
            print(f"✅ Found {len(projects)} projects:")
            for project in projects:
                build_status = "✅ Built" if project["has_build"] else "❌ Not built"
                deps_status = (
                    "✅ Dependencies"
                    if project["has_node_modules"]
                    else "❌ No dependencies"
                )
                print(f"   📦 {project['name']}")
                print(f"      Path: {project['path']}")
                print(f"      Created: {time.ctime(project['created'])}")
                print(f"      {build_status} | {deps_status}")
            return projects
        else:
            print(f"❌ Failed to list projects: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ List projects error: {e}")
        return []


def test_health():
    """Test API health"""
    print("💓 Checking API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API Health: {health['status']}")
            print(f"   Version: {health['version']}")
            print(f"   Timestamp: {time.ctime(health['timestamp'])}")

            for tool, available in health["tools_available"].items():
                status = "✅" if available else "❌"
                print(f"   {status} {tool}")

            return health["status"] == "healthy"
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def run_demo():
    """Run complete demo workflow"""
    print("🚀 Enhanced Code Agent API Demo")
    print("=" * 60)

    # Check API health
    if not test_health():
        print("💡 Make sure the enhanced API is running: python code_agent.py")
        return

    print()

    # Check prerequisites
    if not test_prerequisites():
        print("💡 Please install missing tools and try again")
        return

    print()

    # Generate a test project
    context_path = "../test-demo/context"
    if not os.path.exists(context_path):
        print(f"⚠️  Context path not found: {context_path}")
        context_path = None

    project_name = "test-angular-app"
    project_id = generate_project(
        project_name=project_name,
        context_path=context_path,
        auto_build=True,
        auto_run=False,
    )

    if not project_id:
        return

    print()

    # Monitor generation
    monitor_project_generation(project_id)

    print()

    # List all projects
    list_projects()

    print()
    print("🎉 Demo completed!")
    print()
    print("Next steps:")
    print("1. Navigate to the generated project directory")
    print("2. Run 'ng serve' to start the development server")
    print("3. Open http://localhost:4200 in your browser")


def interactive_mode():
    """Interactive mode for testing"""
    print("🎮 Interactive Enhanced Code Agent Test Mode")
    print("=" * 50)
    print("Commands:")
    print("  1. health - Check API health")
    print("  2. prereq - Check prerequisites")
    print("  3. generate <project_name> [context_path] - Generate project")
    print("  4. status <project_id> - Check project status")
    print("  5. list - List all projects")
    print("  6. demo - Run full demo")
    print("  q. quit")
    print()

    while True:
        try:
            command = input("Enter command: ").strip().split()

            if not command or command[0] == "q":
                break

            if command[0] == "health":
                test_health()
            elif command[0] == "prereq":
                test_prerequisites()
            elif command[0] == "generate" and len(command) >= 2:
                project_name = command[1]
                context_path = command[2] if len(command) > 2 else None
                project_id = generate_project(project_name, context_path)
                if project_id:
                    print(f"Project ID: {project_id}")
            elif command[0] == "status" and len(command) > 1:
                project_id = command[1]
                status = check_project_status(project_id)
                if status:
                    print(json.dumps(status, indent=2))
            elif command[0] == "list":
                list_projects()
            elif command[0] == "demo":
                run_demo()
            else:
                print("❌ Invalid command or missing parameters")

            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        run_demo()

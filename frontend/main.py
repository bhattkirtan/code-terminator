"""Main Streamlit application for AI DevOps Agent Platform."""

import os
import time
import zipfile
from io import BytesIO
from pathlib import Path
from typing import List, Optional

import requests
import streamlit as st
from PIL import Image

from config.settings import settings


# Page configuration
st.set_page_config(
    page_title="AI DevOps Agent Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-processing {
        color: #ffc107;
        font-weight: bold;
    }
    
    .component-preview {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .metrics-container {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class AIDevOpsApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        self.backend_url = f"http://{settings.backend_host}:{settings.backend_port}"
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables."""
        if 'current_task_id' not in st.session_state:
            st.session_state.current_task_id = None
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'generation_status' not in st.session_state:
            st.session_state.generation_status = None
        if 'last_check_time' not in st.session_state:
            st.session_state.last_check_time = 0
    
    def check_backend_health(self) -> bool:
        """Check if backend is healthy."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def render_header(self):
        """Render application header."""
        st.markdown("""
        <div class="main-header">
            <h1>🤖 AI DevOps Agent Platform</h1>
            <p>Transform legacy applications into modern Angular v20 code using AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render sidebar with navigation and status."""
        st.sidebar.title("🛠️ Control Panel")
        
        # Backend health check
        if self.check_backend_health():
            st.sidebar.success("✅ Backend Connected")
            
            # Get backend settings
            try:
                response = requests.get(f"{self.backend_url}/api/settings")
                if response.status_code == 200:
                    settings_data = response.json()
                    st.sidebar.info(f"🎯 Target: {settings_data['target_frameworks'][0]}")
                    
                    # AI model status
                    models = settings_data.get('ai_models', {})
                    st.sidebar.write("🧠 **AI Models:**")
                    for model_type, model_name in models.items():
                        st.sidebar.write(f"- {model_type}: {model_name}")
            except:
                pass
        else:
            st.sidebar.error("❌ Backend Offline")
            st.sidebar.write(f"Backend URL: {self.backend_url}")
        
        # Current task status
        if st.session_state.current_task_id:
            st.sidebar.write("📋 **Current Task:**")
            st.sidebar.code(st.session_state.current_task_id[:8] + "...")
            
            if st.sidebar.button("🔄 Refresh Status"):
                self.update_task_status()
            
            if st.sidebar.button("❌ Cancel Task"):
                self.cancel_current_task()
        
        # Navigation
        st.sidebar.markdown("---")
        page = st.sidebar.radio(
            "📍 Navigation",
            ["🏠 Project Generator", "📊 Task Monitor", "ℹ️ About"]
        )
        
        return page
    
    def render_project_generator(self):
        """Render main project generator interface."""
        st.header("🚀 Generate Angular Project")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Project configuration
            st.subheader("📝 Project Configuration")
            
            project_name = st.text_input(
                "Project Name",
                value="my-modernized-app",
                help="Enter a name for your Angular project"
            )
            
            description = st.text_area(
                "Description (Optional)",
                help="Describe what this application does"
            )
            
            target_framework = st.selectbox(
                "Target Framework",
                ["angular-v20", "angular-v17", "react", "vue"],
                help="Choose the target frontend framework"
            )
            
            additional_requirements = st.text_area(
                "Additional Requirements (Optional)",
                help="Any specific requirements or features needed"
            )
            
            # Screenshot upload
            st.subheader("📷 Upload Screenshots")
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            uploaded_screenshots = st.file_uploader(
                "Select legacy application screenshots",
                type=['png', 'jpg', 'jpeg', 'webp'],
                accept_multiple_files=True,
                help="Upload screenshots of the legacy application UI"
            )
            
            if uploaded_screenshots:
                st.success(f"✅ {len(uploaded_screenshots)} screenshot(s) uploaded")
                
                # Preview screenshots
                if st.checkbox("🔍 Preview Screenshots"):
                    cols = st.columns(min(3, len(uploaded_screenshots)))
                    for i, screenshot in enumerate(uploaded_screenshots):
                        with cols[i % 3]:
                            image = Image.open(screenshot)
                            st.image(image, caption=screenshot.name, use_column_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Reference styles upload
            st.subheader("🎨 Reference Styles (Optional)")
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            uploaded_styles = st.file_uploader(
                "Upload CSS/SCSS files or design references",
                type=['css', 'scss', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Upload style files or design reference images"
            )
            
            if uploaded_styles:
                st.success(f"✅ {len(uploaded_styles)} style file(s) uploaded")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Generate button
            if st.button("🚀 Generate Project", type="primary", use_container_width=True):
                if not uploaded_screenshots:
                    st.error("❌ Please upload at least one screenshot")
                elif not project_name.strip():
                    st.error("❌ Please enter a project name")
                else:
                    self.start_project_generation(
                        project_name,
                        description,
                        target_framework,
                        additional_requirements,
                        uploaded_screenshots,
                        uploaded_styles
                    )
        
        with col2:
            # Status panel
            self.render_status_panel()
    
    def render_status_panel(self):
        """Render project generation status panel."""
        st.subheader("📊 Generation Status")
        
        if st.session_state.current_task_id:
            # Get current status
            status = self.get_task_status(st.session_state.current_task_id)
            
            if status:
                # Progress bar
                progress = status.get('progress', 0) / 100
                st.progress(progress)
                
                # Status display
                status_value = status.get('status', 'unknown')
                if status_value == 'completed':
                    st.markdown('<p class="status-success">✅ Generation Completed!</p>', 
                              unsafe_allow_html=True)
                elif status_value == 'failed':
                    st.markdown('<p class="status-error">❌ Generation Failed</p>', 
                              unsafe_allow_html=True)
                    if status.get('error'):
                        st.error(f"Error: {status['error']}")
                elif status_value == 'processing':
                    st.markdown('<p class="status-processing">⚙️ Processing...</p>', 
                              unsafe_allow_html=True)
                else:
                    st.info(f"Status: {status_value}")
                
                # Current message
                if status.get('message'):
                    st.write(f"**Current Step:** {status['message']}")
                
                # Download button for completed projects
                if status_value == 'completed':
                    if st.button("📥 Download Project", type="primary"):
                        self.download_project(st.session_state.current_task_id)
                    
                    if st.button("👀 Preview Project"):
                        self.show_project_preview(st.session_state.current_task_id)
                
                # Metrics
                if status.get('result'):
                    result = status['result']
                    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
                    st.write("**📈 Generation Metrics:**")
                    if 'components_count' in result:
                        st.write(f"- Components: {result['components_count']}")
                    if 'carbon_emissions' in result:
                        emissions = result['carbon_emissions']
                        st.write(f"- CO₂ Emissions: {emissions.get('total_grams', 0):.2f}g")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Auto-refresh
                if status_value in ['pending', 'processing']:
                    time.sleep(2)
                    st.rerun()
            
        else:
            st.info("🏁 No active generation task")
            st.write("Upload screenshots and click 'Generate Project' to start")
    
    def render_task_monitor(self):
        """Render task monitoring interface."""
        st.header("📊 Task Monitor")
        
        # Current task details
        if st.session_state.current_task_id:
            st.subheader("🔄 Current Task")
            
            status = self.get_task_status(st.session_state.current_task_id)
            if status:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Task ID:** {status['task_id']}")
                    st.write(f"**Status:** {status['status']}")
                    st.write(f"**Progress:** {status['progress']:.1f}%")
                
                with col2:
                    st.write(f"**Created:** {status['created_at']}")
                    st.write(f"**Updated:** {status['updated_at']}")
                    if status.get('error'):
                        st.error(f"**Error:** {status['error']}")
                
                # Detailed progress
                if status.get('message'):
                    st.write(f"**Current Step:** {status['message']}")
                
                # Result details
                if status.get('result'):
                    st.subheader("📋 Results")
                    st.json(status['result'])
        
        else:
            st.info("No active task")
    
    def render_about(self):
        """Render about page."""
        st.header("ℹ️ About AI DevOps Agent Platform")
        
        st.markdown("""
        ### 🎯 Purpose
        This platform uses AI to automatically modernize legacy applications by analyzing screenshots 
        and generating modern Angular v20 code.
        
        ### 🔧 How It Works
        1. **Vision Analysis** - AI analyzes uploaded screenshots to identify UI elements
        2. **Layout Generation** - Converts detected elements to Angular component layouts  
        3. **Code Generation** - Creates complete TypeScript, HTML, and SCSS files
        4. **Style Application** - Applies themes and styling based on reference designs
        5. **Service Stubs** - Generates mock services for easy backend integration
        
        ### 🧠 AI Agents
        - **VisionAgent** - Screenshot analysis using GPT-4 Vision or Claude
        - **LayoutAgent** - Angular v20 layout generation
        - **CodeAgent** - Complete component code generation
        - **StyleAgent** - Theme and styling application
        - **StubAgent** - Service mock generation
        
        ### ⚡ Features
        - Modern Angular v20 code generation
        - Responsive design implementation
        - Accessibility best practices
        - Service stub generation
        - Carbon emission tracking
        - Real-time progress monitoring
        
        ### 🔗 Technology Stack
        - **Frontend:** Streamlit
        - **Backend:** FastAPI
        - **AI Models:** OpenAI GPT-4, Anthropic Claude
        - **Target Framework:** Angular v20
        """)
        
        # System status
        st.subheader("🔧 System Status")
        
        health_status = self.check_backend_health()
        if health_status:
            st.success("✅ All systems operational")
        else:
            st.error("❌ Backend connection issues")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Backend URL:** {self.backend_url}")
        with col2:
            st.info(f"**Frontend Port:** {settings.streamlit_port}")
    
    def start_project_generation(
        self, 
        project_name: str,
        description: str,
        target_framework: str,
        additional_requirements: str,
        screenshots: List,
        styles: Optional[List] = None
    ):
        """Start project generation process."""
        try:
            # Prepare files for upload
            files = []
            for screenshot in screenshots:
                files.append(('screenshots', (screenshot.name, screenshot.getvalue(), screenshot.type)))
            
            if styles:
                for style_file in styles:
                    files.append(('reference_styles', (style_file.name, style_file.getvalue(), style_file.type)))
            
            # Prepare data
            data = {
                'project_name': project_name,
                'target_framework': target_framework,
                'description': description,
                'additional_requirements': additional_requirements
            }
            
            # Make request
            response = requests.post(
                f"{self.backend_url}/api/projects/generate",
                data=data,
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.current_task_id = result['task_id']
                st.success(f"✅ Project generation started! Task ID: {result['task_id'][:8]}...")
                st.rerun()
            else:
                st.error(f"❌ Failed to start generation: {response.text}")
                
        except Exception as e:
            st.error(f"❌ Error starting generation: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get task status from backend."""
        try:
            response = requests.get(f"{self.backend_url}/api/tasks/{task_id}")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def update_task_status(self):
        """Update current task status."""
        if st.session_state.current_task_id:
            status = self.get_task_status(st.session_state.current_task_id)
            if status:
                st.session_state.generation_status = status
                st.rerun()
    
    def cancel_current_task(self):
        """Cancel the current task."""
        if st.session_state.current_task_id:
            try:
                response = requests.delete(f"{self.backend_url}/api/tasks/{st.session_state.current_task_id}")
                if response.status_code == 200:
                    st.success("✅ Task cancelled")
                    st.session_state.current_task_id = None
                    st.rerun()
                else:
                    st.error("❌ Failed to cancel task")
            except Exception as e:
                st.error(f"❌ Error cancelling task: {str(e)}")
    
    def download_project(self, task_id: str):
        """Download generated project."""
        try:
            response = requests.get(f"{self.backend_url}/api/projects/{task_id}/download")
            if response.status_code == 200:
                st.download_button(
                    label="📁 Download ZIP File",
                    data=response.content,
                    file_name=f"generated-project-{task_id[:8]}.zip",
                    mime="application/zip"
                )
            else:
                st.error("❌ Failed to download project")
        except Exception as e:
            st.error(f"❌ Error downloading project: {str(e)}")
    
    def show_project_preview(self, task_id: str):
        """Show project structure preview."""
        try:
            response = requests.get(f"{self.backend_url}/api/projects/{task_id}/preview")
            if response.status_code == 200:
                preview = response.json()
                
                st.subheader("📁 Project Structure")
                st.json(preview.get('structure', {}))
                
                if preview.get('stats'):
                    st.subheader("📊 Generation Statistics")
                    st.json(preview['stats'])
            else:
                st.error("❌ Failed to load preview")
        except Exception as e:
            st.error(f"❌ Error loading preview: {str(e)}")
    
    def run(self):
        """Run the Streamlit application."""
        self.render_header()
        
        # Sidebar navigation
        page = self.render_sidebar()
        
        # Main content based on navigation
        if page == "🏠 Project Generator":
            self.render_project_generator()
        elif page == "📊 Task Monitor":
            self.render_task_monitor()
        elif page == "ℹ️ About":
            self.render_about()


def main():
    """Main application entry point."""
    app = AIDevOpsApp()
    app.run()


if __name__ == "__main__":
    main()
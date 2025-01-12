# Home.py
import streamlit as st
from db.schema import init_db #, migrate_existing_data

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


st.set_page_config(
    page_title="Translation Management System",
    page_icon="🌐",
    layout="wide"
)

def main():
    st.title("Translation Management System")
    
    st.markdown("""
    Welcome to the Translation Management System! 👋
    
    ### Available Pages:
    1. **Translation** - Translate texts using multiple providers
    2. **Search and Edit** - View and modify previous translations
    3. **Export** - Export translations to CSV
    4. **Report Generation** - Generate complete translation reports
    
    ### Current Project
    """)
    
    # Project selection in sidebar
    with st.sidebar:
        st.title("Project Settings")
        if 'current_project' not in st.session_state:
            st.session_state.current_project = "Default Project"
        
        # Get projects from database
        from db.database import TranslationDB
        db = TranslationDB()
        projects = db.get_projects()
        
        # Add "Create New Project" option
        selected_project = st.selectbox(
            "Select Project",
            ["Create New Project"] + projects,
            index=projects.index(st.session_state.current_project) + 1 if st.session_state.current_project in projects else 0
        )
        
        if selected_project == "Create New Project":
            new_project = st.text_input("Enter Project Name")
            if st.button("Create Project") and new_project:
                st.session_state.current_project = new_project
                st.rerun()
        else:
            st.session_state.current_project = selected_project
    
    # Display current project info
    st.subheader(f"Current Project: {st.session_state.current_project}")
    
    # Project statistics
    if st.session_state.current_project:
        translations = db.get_translations(st.session_state.current_project)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Translations", len(translations))
        with col2:
            completed = sum(1 for t in translations if t[3])  # target_text is not None
            st.metric("Completed", completed)
        with col3:
            st.metric("Pending", len(translations) - completed)

if __name__ == "__main__":
    # Initialize database with new schema
    init_db()
    # migrate_existing_data()
    main()
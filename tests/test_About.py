from streamlit.testing.v1 import AppTest
import os

def test_about_page():
    # Create an instance of AppTest
    at = AppTest.from_file("pages/about.py")
    
    # Run the app
    at.run()
    
    # Get all markdown elements
    markdown_elements = at.markdown
    
    # Ensure there is at least one markdown element
    assert len(markdown_elements) > 0

def test_about_page_markdown_options():
    at = AppTest.from_file("pages/about.py")
    at.run()
    
    # Get all markdown elements
    markdown_elements = at.markdown
    
    # Check if markdown is rendered with unsafe_allow_html=True
    for element in markdown_elements:
        assert element.allow_html is True

def test_about_page_content_not_empty():
    at = AppTest.from_file("pages/about.py")
    at.run()
    
    # Get all markdown elements
    markdown_elements = at.markdown
    
    # Verify that the content is not empty
    for element in markdown_elements:
        assert element.value.strip() != ""

def test_about_page_session_state():
    at = AppTest.from_file("pages/about.py")
    at.run()
    
    # Verify the session state is maintained
    assert at.session_state is not None

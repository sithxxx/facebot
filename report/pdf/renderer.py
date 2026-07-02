import os
import logging
from weasyprint import HTML, CSS

def render_pdf(html_content: str, output_path: str) -> str:
    """
    Converts HTML string to PDF using WeasyPrint.
    """
    try:
        # Resolve templates dir for base_url (if needed for assets, though we use base64 here)
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        
        # We can add a custom CSS string for print adjustments if needed
        print_css = CSS(string='''
            @page {
                size: A4;
                margin: 0;
            }
        ''')
        
        # Render
        HTML(string=html_content, base_url=templates_dir).write_pdf(
            output_path,
            stylesheets=[print_css]
        )
        
        # Log size
        if os.path.exists(output_path):
            size_kb = os.path.getsize(output_path) / 1024
            logging.info(f"Successfully rendered PDF: {output_path} ({size_kb:.1f} KB)")
            return output_path
        else:
            raise RuntimeError(f"WeasyPrint finished but file not found at {output_path}")
            
    except Exception as e:
        logging.error(f"WeasyPrint rendering failed: {e}")
        raise RuntimeError(f"Failed to render PDF: {e}")

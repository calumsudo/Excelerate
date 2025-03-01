# app/utils/export_portfolios.py

import sys
from pathlib import Path
import logging
import tkinter as tk
from tkinter import messagebox

# Add the parent directory to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Now import project modules after adjusting sys.path
# ruff: noqa: E402
from config.system_config import SystemConfig
from managers.file_manager import PortfolioFileManager
from managers.portfolio import Portfolio

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def export_portfolio(portfolio: Portfolio, logger=None):
    """Export portfolio to desktop"""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    try:
        # Get application directory
        config_dir = SystemConfig.get_app_directory()
        
        # Initialize file manager
        file_manager = PortfolioFileManager(config_dir)
        
        # Export the portfolio
        result = file_manager.export_portfolio_workbook(portfolio)
        
        if result:
            logger.info(f"Successfully exported {portfolio.value} portfolio to {result}")
            return True, result
        else:
            logger.error(f"Failed to export {portfolio.value} portfolio")
            return False, None
            
    except Exception as e:
        if logger:
            logger.error(f"Error exporting portfolio: {str(e)}")
        return False, str(e)

def gui_export():
    """Create a simple GUI for exporting portfolios"""
    # Create root window
    root = tk.Tk()
    root.title("Export Portfolios")
    root.geometry("400x200")
    
    # Setup logging
    logger = setup_logging()
    
    # Create interface
    header = tk.Label(root, text="Export Portfolio Workbooks", font=("Helvetica", 14, "bold"))
    header.pack(pady=20)
    
    # Export buttons
    alder_btn = tk.Button(root, text="Export Alder Portfolio to Desktop", 
                         command=lambda: export_and_show_result(Portfolio.ALDER))
    alder_btn.pack(pady=5)
    
    wr_btn = tk.Button(root, text="Export White Rabbit Portfolio to Desktop",
                      command=lambda: export_and_show_result(Portfolio.WHITE_RABBIT))
    wr_btn.pack(pady=5)
    
    # Status label
    status_label = tk.Label(root, text="")
    status_label.pack(pady=10)
    
    def export_and_show_result(portfolio):
        """Export and display result"""
        status_label.config(text=f"Exporting {portfolio.value} portfolio...")
        root.update()
        
        success, result = export_portfolio(portfolio, logger)
        
        if success:
            status_label.config(text=f"Exported to:\n{result}")
            messagebox.showinfo("Success", f"Portfolio exported to:\n{result}")
        else:
            status_label.config(text=f"Failed: {result}")
            messagebox.showerror("Error", f"Export failed: {result}")
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        # Command line mode
        logger = setup_logging()
        
        if sys.argv[1].lower() in ["alder", "a"]:
            success, result = export_portfolio(Portfolio.ALDER, logger)
            if not success:
                sys.exit(1)
        elif sys.argv[1].lower() in ["whiterabbit", "wr", "w"]:
            success, result = export_portfolio(Portfolio.WHITE_RABBIT, logger)
            if not success:
                sys.exit(1)
        else:
            print("Usage: python export_portfolios.py [alder|whiterabbit]")
            print("Or run without arguments to use GUI")
            sys.exit(1)
    else:
        # GUI mode
        gui_export()
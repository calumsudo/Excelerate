# app/gui/file_explorer.py
import customtkinter as ctk
from pathlib import Path
import pandas as pd
from tkinter import ttk
import shutil
from .base_window import BasePage
from managers.portfolio import Portfolio
from datetime import datetime
import sqlite3
from typing import List, Dict


class FileFilter:
    def __init__(self):
        self.portfolio = "All"
        self.funder = "All"
        self.file_type = "All"  # "Uploaded", "Pivot", "All"
        self.date_range = None  # Tuple of (start_date, end_date)
        self.search_text = ""


class FileExplorer(BasePage):
    def get_portfolio(self) -> Portfolio:
        return None

    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(header, text="File Explorer", font=("Helvetica", 24, "bold")).pack(
            side="left", padx=10
        )

        # Create Filter Section
        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.setup_filter_section(filter_frame)

        # Main content area
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=5)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Search bar
        search_frame = ctk.CTkFrame(content)
        search_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_changed)

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search files...",
            textvariable=self.search_var,
            width=300,
        )
        search_entry.pack(side="left", padx=5, fill="x", expand=True)

        refresh_btn = ctk.CTkButton(
            search_frame, text="🔄 Refresh", width=100, command=self.refresh_files
        )
        refresh_btn.pack(side="right", padx=5)

        # File list frame
        list_frame = ctk.CTkFrame(content)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)

        # Create file list with columns
        columns = ("Filename", "Portfolio", "Funder", "Type", "Date", "Status")
        self.file_list = ttk.Treeview(list_frame, columns=columns, show="headings")

        # Configure columns
        self.file_list.heading(
            "Filename", text="Filename", command=lambda: self.sort_column("Filename")
        )
        self.file_list.heading(
            "Portfolio", text="Portfolio", command=lambda: self.sort_column("Portfolio")
        )
        self.file_list.heading(
            "Funder", text="Funder", command=lambda: self.sort_column("Funder")
        )
        self.file_list.heading(
            "Type", text="Type", command=lambda: self.sort_column("Type")
        )
        self.file_list.heading(
            "Date", text="Date", command=lambda: self.sort_column("Date")
        )
        self.file_list.heading(
            "Status", text="Status", command=lambda: self.sort_column("Status")
        )

        # Set column widths
        self.file_list.column("Filename", width=300)
        self.file_list.column("Portfolio", width=100)
        self.file_list.column("Funder", width=100)
        self.file_list.column("Type", width=100)
        self.file_list.column("Date", width=100)
        self.file_list.column("Status", width=100)

        self.file_list.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars
        y_scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.file_list.yview
        )
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(
            list_frame, orient="horizontal", command=self.file_list.xview
        )
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.file_list.configure(
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
        )

        # Preview frame
        self.preview_frame = ctk.CTkFrame(content)
        self.preview_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)

        # Preview header
        preview_header = ctk.CTkFrame(self.preview_frame)
        preview_header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.file_label = ctk.CTkLabel(
            preview_header, text="No file selected", font=("Helvetica", 16)
        )
        self.file_label.pack(side="left", padx=10)

        # Export button
        self.export_button = ctk.CTkButton(
            preview_header,
            text="Export File",
            command=self.export_file,
            state="disabled",
        )
        self.export_button.pack(side="right", padx=10)

        # Preview table
        self.preview_table = ttk.Treeview(self.preview_frame, show="headings")
        self.preview_table.grid(row=1, column=0, sticky="nsew")

        # Preview scrollbars
        preview_y_scroll = ttk.Scrollbar(
            self.preview_frame, orient="vertical", command=self.preview_table.yview
        )
        preview_y_scroll.grid(row=1, column=1, sticky="ns")
        preview_x_scroll = ttk.Scrollbar(
            self.preview_frame, orient="horizontal", command=self.preview_table.xview
        )
        preview_x_scroll.grid(row=2, column=0, sticky="ew")

        self.preview_table.configure(
            yscrollcommand=preview_y_scroll.set, xscrollcommand=preview_x_scroll.set
        )

        # Initialize filter state
        self.filter_state = FileFilter()

        # Bind selection event
        self.file_list.bind("<<TreeviewSelect>>", self.on_file_selected)

        # Initial load
        self.refresh_files()

    def setup_filter_section(self, frame):
        """Setup the filter sidebar"""
        frame.grid_columnconfigure(0, weight=1)

        # Portfolio Filter
        ctk.CTkLabel(frame, text="Portfolio", font=("Helvetica", 12, "bold")).pack(
            pady=(10, 5), padx=10
        )
        self.portfolio_var = ctk.StringVar(value="All")
        portfolio_menu = ctk.CTkOptionMenu(
            frame,
            values=["All"] + [p.value for p in Portfolio],
            variable=self.portfolio_var,
            command=self.apply_filters,
        )
        portfolio_menu.pack(pady=5, padx=10, fill="x")

        # Funder Filter
        ctk.CTkLabel(frame, text="Funder", font=("Helvetica", 12, "bold")).pack(
            pady=(10, 5), padx=10
        )
        self.funder_var = ctk.StringVar(value="All")
        self.funder_menu = ctk.CTkOptionMenu(
            frame,
            values=self.get_available_funders(),
            variable=self.funder_var,
            command=self.apply_filters,
        )
        self.funder_menu.pack(pady=5, padx=10, fill="x")

        # File Type Filter
        ctk.CTkLabel(frame, text="File Type", font=("Helvetica", 12, "bold")).pack(
            pady=(10, 5), padx=10
        )
        self.file_type_var = ctk.StringVar(value="All")
        file_type_menu = ctk.CTkOptionMenu(
            frame,
            values=["All", "Uploaded", "Pivot Tables"],
            variable=self.file_type_var,
            command=self.apply_filters,
        )
        file_type_menu.pack(pady=5, padx=10, fill="x")

        # Date Range Filter
        ctk.CTkLabel(frame, text="Date Range", font=("Helvetica", 12, "bold")).pack(
            pady=(10, 5), padx=10
        )

        # Start Date
        self.start_date = ctk.CTkEntry(
            frame, placeholder_text="Start Date (YYYY-MM-DD)"
        )
        self.start_date.pack(pady=5, padx=10, fill="x")

        # End Date
        self.end_date = ctk.CTkEntry(frame, placeholder_text="End Date (YYYY-MM-DD)")
        self.end_date.pack(pady=5, padx=10, fill="x")

        # Apply Date Filter Button
        ctk.CTkButton(frame, text="Apply Date Filter", command=self.apply_filters).pack(
            pady=10, padx=10, fill="x"
        )

        # Reset Filters Button
        ctk.CTkButton(
            frame, text="Reset Filters", command=self.reset_filters, fg_color="grey"
        ).pack(pady=(20, 10), padx=10, fill="x")

    def get_available_funders(self) -> List[str]:
        """Get unique funders from database"""
        try:
            with sqlite3.connect(self.controller.file_manager.db_path) as conn:
                cursor = conn.execute("SELECT DISTINCT funder FROM uploaded_files")
                funders = [row[0] for row in cursor.fetchall()]
                return ["All"] + sorted(funders)
        except Exception as e:
            self.show_error(f"Error getting funders: {str(e)}")
            return ["All"]

    def apply_filters(self, *args):
        """Apply all current filters"""
        self.filter_state.portfolio = self.portfolio_var.get()
        self.filter_state.funder = self.funder_var.get()
        self.filter_state.file_type = self.file_type_var.get()

        try:
            start = (
                datetime.strptime(self.start_date.get(), "%Y-%m-%d")
                if self.start_date.get()
                else None
            )
            end = (
                datetime.strptime(self.end_date.get(), "%Y-%m-%d")
                if self.end_date.get()
                else None
            )
            self.filter_state.date_range = (start, end) if start and end else None
        except ValueError:
            self.show_error("Invalid date format. Use YYYY-MM-DD")
            return

        self.refresh_files()

    def reset_filters(self):
        """Reset all filters to default values"""
        self.portfolio_var.set("All")
        self.funder_var.set("All")
        self.file_type_var.set("All")
        self.start_date.delete(0, "end")
        self.end_date.delete(0, "end")
        self.search_var.set("")
        self.filter_state = FileFilter()
        self.refresh_files()

    def on_search_changed(self, *args):
        """Handle search text changes"""
        self.filter_state.search_text = self.search_var.get()
        self.refresh_files()

    def get_filtered_files(self) -> List[Dict]:
        """Get filtered files from database"""
        try:
            # Base query for uploaded files
            uploaded_query = """
                SELECT 
                    uf.original_filename,
                    uf.stored_filename,
                    uf.portfolio,
                    uf.funder,
                    uf.upload_date,
                    uf.processing_status,
                    uf.file_path,
                    'Uploaded' as file_type
                FROM uploaded_files uf
                WHERE 1=1
            """

            # Base query for pivot tables
            pivot_query = """
                SELECT 
                    pt.stored_filename as original_filename,
                    pt.stored_filename,
                    pt.portfolio,
                    pt.funder,
                    pt.creation_date as upload_date,
                    'completed' as processing_status,
                    pt.file_path,
                    'Pivot Tables' as file_type
                FROM pivot_tables pt
                WHERE 1=1
            """

            params = []

            # Add filter conditions
            if self.filter_state.portfolio != "All":
                uploaded_query += " AND uf.portfolio = ?"
                pivot_query += " AND pt.portfolio = ?"
                params.append(self.filter_state.portfolio)
                params.append(self.filter_state.portfolio)

            if self.filter_state.funder != "All":
                uploaded_query += " AND uf.funder = ?"
                pivot_query += " AND pt.funder = ?"
                params.append(self.filter_state.funder)
                params.append(self.filter_state.funder)

            if self.filter_state.date_range:
                start, end = self.filter_state.date_range
                uploaded_query += (
                    " AND DATE(uf.upload_date) BETWEEN DATE(?) AND DATE(?)"
                )
                pivot_query += " AND DATE(pt.creation_date) BETWEEN DATE(?) AND DATE(?)"
                params.extend([start.isoformat(), end.isoformat()])
                params.extend([start.isoformat(), end.isoformat()])

            if self.filter_state.search_text:
                search_term = f"%{self.filter_state.search_text}%"
                uploaded_query += """ AND (
                    uf.original_filename LIKE ? 
                    OR uf.portfolio LIKE ? 
                    OR uf.funder LIKE ?
                )"""
                pivot_query += """ AND (
                    pt.stored_filename LIKE ? 
                    OR pt.portfolio LIKE ? 
                    OR pt.funder LIKE ?
                )"""
                params.extend([search_term, search_term, search_term])
                params.extend([search_term, search_term, search_term])

            # Combine queries based on file type filter
            if self.filter_state.file_type == "Uploaded":
                final_query = uploaded_query
                final_params = params[
                    : len(params) // 2
                ]  # Use only first set of params
            elif self.filter_state.file_type == "Pivot Tables":
                final_query = pivot_query
                final_params = params[
                    len(params) // 2 :
                ]  # Use only second set of params
            else:  # "All"
                final_query = f"{uploaded_query} UNION ALL {pivot_query}"
                final_params = params

            final_query += " ORDER BY upload_date DESC"

            with sqlite3.connect(self.controller.file_manager.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(final_query, final_params)
                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            self.show_error(f"Error getting files: {str(e)}")
            return []

    def refresh_files(self):
        """Refresh the file list with current filters"""
        # Clear existing items
        for item in self.file_list.get_children():
            self.file_list.delete(item)

        # Get filtered files
        files = self.get_filtered_files()

        # Add files to list
        for file in files:
            try:
                date = datetime.fromisoformat(file["upload_date"]).strftime("%Y-%m-%d")
            except ValueError:
                date = "Unknown"

            # If file path exists and is valid
            file_path = file.get("file_path")
            if file_path and Path(file_path).exists():
                self.file_list.insert(
                    "",
                    "end",
                    values=(
                        file["original_filename"],
                        file["portfolio"],
                        file["funder"],
                        file["file_type"],
                        date,
                        file["processing_status"],
                    ),
                    tags=(str(file_path),),
                )

    def sort_column(self, column):
        """Sort treeview by column"""
        items = [
            (self.file_list.set(item, column), item)
            for item in self.file_list.get_children("")
        ]

        # Check if we're reversing the sort
        reverse = False
        if hasattr(self, "_sort_column") and self._sort_column == column:
            reverse = not getattr(self, "_sort_reverse", False)

        # Store sort state
        self._sort_column = column
        self._sort_reverse = reverse

        # Sort items
        items.sort(reverse=reverse)
        for idx, (_, item) in enumerate(items):
            self.file_list.move(item, "", idx)

        # Update column headers to show sort direction
        for col in self.file_list["columns"]:
            if col == column:
                self.file_list.heading(col, text=f"{col} {'↓' if reverse else '↑'}")
            else:
                self.file_list.heading(col, text=col)

    def on_file_selected(self, event):
        """Handle file selection"""
        selection = self.file_list.selection()
        if not selection:
            self.clear_preview()
            return

        # Get file path from item tags
        item = selection[0]
        file_path = self.file_list.item(item)["tags"][0]
        if not file_path:
            self.clear_preview()
            return

        self.current_file = Path(file_path)
        self.file_label.configure(text=self.current_file.name)
        self.export_button.configure(state="normal")

        self.preview_file(self.current_file)

    def preview_file(self, file_path: Path):
        """Preview CSV or Excel file content"""
        try:
            # Clear existing preview
            for item in self.preview_table.get_children():
                self.preview_table.delete(item)
            self.preview_table["columns"] = ()

            # Read file based on type
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() == ".xlsx":
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file type")

            # Configure columns
            columns = list(df.columns)
            self.preview_table["columns"] = columns

            # Hide the default first column (tree column)
            self.preview_table["show"] = "headings"

            # Configure column headings and widths
            for col in columns:
                self.preview_table.heading(col, text=col)
                # Calculate column width based on data
                max_width = max(
                    len(str(col)),
                    df[col].astype(str).str.len().max() if len(df) > 0 else 0,
                )
                self.preview_table.column(
                    col, width=min(max_width * 10, 300)
                )  # Scale width, max 300px

            # Add data rows (limit to first 1000 rows for performance)
            for idx, row in df.head(1000).iterrows():
                values = [str(val) for val in row]
                self.preview_table.insert("", "end", values=values)

            # Show row count info
            total_rows = len(df)
            shown_rows = min(1000, total_rows)
            if total_rows > 1000:
                self.file_label.configure(
                    text=f"{self.current_file.name} (Showing {shown_rows:,} of {total_rows:,} rows)"
                )

        except Exception as e:
            self.show_error(f"Error previewing file: {str(e)}")

    def export_file(self):
        """Export selected file to user-chosen location"""
        if not hasattr(self, "current_file"):
            return

        # Get destination path
        file_types = [("All Files", "*.*")]
        if self.current_file.suffix.lower() == ".csv":
            file_types = [("CSV Files", "*.csv")] + file_types
        elif self.current_file.suffix.lower() == ".xlsx":
            file_types = [("Excel Files", "*.xlsx")] + file_types

        dest_path = ctk.filedialog.asksaveasfilename(
            defaultextension=self.current_file.suffix,
            filetypes=file_types,
            initialfile=self.current_file.name,
        )

        if dest_path:
            try:
                shutil.copy2(self.current_file, dest_path)
                self.show_info(f"File exported successfully to:\n{dest_path}")
            except Exception as e:
                self.show_error(f"Error exporting file: {str(e)}")

    def clear_preview(self):
        """Clear the preview area"""
        self.file_label.configure(text="No file selected")
        self.export_button.configure(state="disabled")
        for item in self.preview_table.get_children():
            self.preview_table.delete(item)
        self.preview_table["columns"] = ()

    def show_error(self, message: str):
        """Show error message"""
        import tkinter.messagebox as tkmb

        tkmb.showerror("Error", message)

    def show_info(self, message: str):
        """Show info message"""
        import tkinter.messagebox as tkmb

        tkmb.showinfo("Information", message)

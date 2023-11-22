import pandas as pd

    
def current_total_records(info: str) -> tuple:
    """Returns values used in metrics

    Args:
        info (str): accepts 'total', 'loss', or 'theft'

    Returns:
        tuple: current_date, current_total, new_records, delta_color, sign
    """
    
        # Colors
    clr_outlier = "#e54848"
    clr_font = "#dedede"
    
    date_report_total = pd.read_parquet("assets/models/date-report-total.parquet.gzip")
    
    if info == "total":
        
        current_yr_records = date_report_total[
            date_report_total["date"].dt.year == date_report_total["date"].dt.year.max()
        ]
        current_mo_records = current_yr_records[
            current_yr_records['date'].dt.month == current_yr_records['date'].dt.month.max()
        ]
        
        current_total = current_yr_records["total"].sum()
        new_records = current_mo_records["total"].sum()
        
    elif info == "theft":
        
        current_yr_records = date_report_total[
            (date_report_total["date"].dt.year == date_report_total["date"].dt.year.max())&
            (date_report_total["report"] == "Theft")
        ]
        current_mo_records = current_yr_records[
            (current_yr_records['date'].dt.month == current_yr_records['date'].dt.month.max())&
            (current_yr_records["report"] == "Theft")
        ]
        
        current_total = current_yr_records["total"].sum()
        new_records = current_mo_records["total"].sum()
        
    elif info == "loss":
        
        current_yr_records = date_report_total[
            (date_report_total["date"].dt.year == date_report_total["date"].dt.year.max())&
            (date_report_total["report"] == "Loss")
        ]
        current_mo_records = current_yr_records[
            (current_yr_records['date'].dt.month == current_yr_records['date'].dt.month.max())&
            (current_yr_records["report"] == "Loss")
        ]
        
        current_total = current_yr_records["total"].sum()
        new_records = current_mo_records["total"].sum()
        

    if new_records == 0:
        delta_color = clr_font
        sign = ""
        
    else:
        delta_color = clr_outlier
        sign = "+"
        
    current_date = date_report_total["date"].dt.year.max()
    
    return current_date, current_total, new_records, delta_color, sign

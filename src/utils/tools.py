import os
import time

# File modification date
def modification_date(file, granularity):
    """Returns date when file was last modified at

    Args:
        file (str): file path 
        granularity (str): temporal granularity. Possible values year, month, day, date. 
        
        'date' has the following format YYYY-MM-DD

    Returns:
        str: file modification date (numerical format)
    """
    t = os.path.getmtime(file)
    year, month, day, hour, minute, second = time.localtime(t)[:-3]
    
    date=None
    
    if granularity == "year":
        date = f"{year}"
    elif granularity == "month":
        date = f"{month}"
    elif granularity == "day":
        date = f"{day}"
    elif granularity == "date":
        date = f"{year}-{month}-{day}"
        
    return date
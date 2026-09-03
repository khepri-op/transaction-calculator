import io
import csv
import streamlit as st
from datetime import datetime

# --- Memory Setup for Auto-Clearing ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "error_message" not in st.session_state:
    st.session_state.error_message = False

st.set_page_config(page_title="BharatPe Calculator", page_icon="🧾")
st.title("🧾 BharatPe Total Calculator")
st.write("Upload your BharatPe CSV files below to calculate the total.")

# --- Display the Error Message ---
# If we just cleared invalid files, this will show a warning
if st.session_state.error_message:
    st.error("⚠️ Invalid files detected! The upload box has been cleared. Please upload valid PDF statements only.")
    st.session_state.error_message = False # Reset it so it disappears next time


# --- 3. The Uploader with a Dynamic Key ---
# Notice the "key" argument. This is how we force it to clear later.
uploaded_files = st.file_uploader(
    "Tap here to select CSVs", 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)

def get_date_range(_date_list):
    """Retrive the date objects of the start and end of the transactions and format them to a name
    so it can be used as a filename"""

    month = ""
    
    # Remove duplicates
    date_list = list(dict.fromkeys(_date_list)) 
       
    # Get the start and end date objects
    start_date = datetime.strptime(date_list[0], "%Y-%m-%d %H:%M:%S")
    end_date = datetime.strptime(date_list[-1], "%Y-%m-%d %H:%M:%S")
    
    # Find out if the date range corresponds exactly to a month
    if (start_date.month == end_date.month) and ((end_date.day - start_date.day) in [30, 29, 28, 27]):
        month = start_date.strftime("%B")
    else:
        month = 'none'
    
    # Store them in a neatly formatted string. eg - August 16 2026
    date_range = {
        'start': f"{start_date.strftime("%b")}-{start_date.day}-{start_date.year}",
        'end': f"{end_date.strftime("%b")}-{end_date.day}-{end_date.year}",
        'month': month,
    }
    return date_range
    
def add_transactions(_list):
    total = 0
    for t in _list:
        total += float(t)
    
    return total

def extract_csv(csv_file):
    """Parses the csv to get sum of all transactions and information to make the file name
    from the start and end dates"""
    
    transactions, dates = [], []
    #Load the text from the csv into the memory and store in stringio
    stringio = io.StringIO(csv_file.getvalue().decode('utf-8', errors='ignore'))
    reader = csv.reader(stringio)
    header = next(reader)
    
    date_idx = header.index('Transaction Date and Time')
    transaction_idx = header.index('Amount Added')
    
    # Parse the csv and collect each transaction amount row by row
    for row in reader:
        if row:
            dates.append(row[date_idx])
            transactions.append(row[transaction_idx])

    # Pass the whole date list to parse the start and end of the transactions in the csv
    date_range = get_date_range(dates)
    
    information = {
        'start': date_range['start'],
        'end': date_range['end'],
        'month': date_range['month'],
        'total': add_transactions(transactions),
    }
    
    #Return the dict full of info 
    return information        


def format_indian_style(number):
    """Formats an int with commans in indian style"""
    # 1. Convert number to string, then into a list of characters
    char_list = list(str(number))

    # 2. Track our position from the right side and store our final pieces
    result = []
    digits_seen = 0

    # Loop backwards through the list of characters
    for char in reversed(char_list):
        
        # Check if we need to add a comma BEFORE adding the next digit
        if digits_seen == 3:
            result.append(',')
        elif digits_seen > 3 and (digits_seen - 3) % 2 == 0:
            result.append(',')
            
        # Add the current character
        result.append(char)
        digits_seen += 1

    # 3. Since we built it backwards, reverse it and join it into a final string
    result.reverse()
    formatted_string = "".join(result)

    return formatted_string
    
if uploaded_files: 
    valid_csv = []
    
    # We only keep files that end in .csv
    for file in uploaded_files:
        if file.name.lower().endswith('.csv'):
            valid_csv.append(file)
            
    # --- If NO valid CSVs were found, clear everything ---
    if len(valid_csv) == 0:
        st.session_state.error_message = True  # Trigger the red error message
        st.session_state.uploader_key += 1     # Change the key to reset the uploader
        st.rerun()                             # Refresh the website instantly
    
    
    if len(valid_csv) > 0:
        #Add the Calculate Button
        if st.button("CALCULATE", type="primary"):
            all_files_transactions = 0
        
            # Draw a line separator
            st.markdown("---")
            
            for file in valid_csv:
                try:
                    info = extract_csv(csv_file=file)
                    
                    # Form a clean name for the file
                    if info['month'] != 'none':
                        clean_name = f":orange[{info['month']}]"
                    else:
                        clean_name = f":orange[{info['start']}] ➡️ :orange[{info['end']}]"
                         
                    total = int(info['total'])
                    # Big text for individual files
                    st.subheader(f"📄 {clean_name} Total: :red[₹{format_indian_style(total)}]")
                    all_files_transactions += info['total']
            
                except Exception as e:
                    # Safely show errors on the website without crashing the server
                    st.error(f"Error processing {file.name}: {e}")

            # Massive text for the Grand Total
            st.markdown("---")
            
            total_sum = format_indian_style(int(all_files_transactions))     
            st.header(f":green[GRAND TOTAL] for all files: :red[₹{total_sum}]")

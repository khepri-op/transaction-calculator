import pdfplumber
import re
import streamlit as st

# --- 1. Memory Setup for Auto-Clearing ---
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "error_message" not in st.session_state:
    st.session_state.error_message = False

st.set_page_config(page_title="BharatPe Calculator", page_icon="🧾")
st.title("🧾 BharatPe Total Calculator")
st.write("Upload your BharatPe PDF files below to calculate the total.")

# --- 2. Display the Error Message ---
# If we just cleared invalid files, this will show a warning
if st.session_state.error_message:
    st.error("⚠️ Invalid files detected! The upload box has been cleared. Please upload valid PDF statements only.")
    st.session_state.error_message = False # Reset it so it disappears next time


# --- 3. The Uploader with a Dynamic Key ---
# Notice the "key" argument. This is how we force it to clear later.
uploaded_files = st.file_uploader(
    "Tap here to select PDFs", 
    type="pdf", 
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}"
)


def extract_list(_pdf_file):
    full_text = ""
    with pdfplumber.open(_pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text
            
    flat_text = full_text.replace('\n', ' ')

    pattern = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}.*?[\d,]+\.\d+\s+[\d,]+\.\d+\s+([\d,]+\.\d+)'
    matches_list = re.findall(pattern, flat_text)
    
    #Returns a list of all transactions
    return matches_list

def add_transactions(_list):
    total = 0
    for t in _list:
        total += float(t)
    
    return total

def format_indian_style(number):
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
    valid_pdfs = []
    
    # --- 4. Ignore invalid files ---
    # We only keep files that end in .pdf
    for file in uploaded_files:
        if file.name.lower().endswith('.pdf'):
            valid_pdfs.append(file)
            
    # --- 5. If NO valid PDFs were found, clear everything ---
    if len(valid_pdfs) == 0:
        st.session_state.error_message = True  # Trigger the red error message
        st.session_state.uploader_key += 1     # Change the key to reset the uploader
        st.rerun()                             # Refresh the website instantly
    
    
    if len(valid_pdfs) > 0:
        #Add the Calculate Button
        if st.button("Calculate Totals", type="primary"):
            total_transactions_sum = 0
        
            # Draw a line separator
            st.markdown("---")
            
            for file in valid_pdfs:
                try:
                    transactions = extract_list(file)
                    months_sum = add_transactions(transactions)
                    
                    # 2. Fix the file name extraction
                    clean_name = file.name.replace('.pdf', '').title()
                    
                    # 3. Big text for individual files
                    st.subheader(f"📄 {clean_name}'s Total: ₹{format_indian_style(int(months_sum))}")
                    
                    total_transactions_sum += months_sum
            
                except Exception as e:
                    # Safely show errors on the website without crashing the server
                    st.error(f"Error processing {file.name}: {e}")

            # 4. Massive text for the Grand Total
            st.markdown("---")
            
            total_sum = format_indian_style(int(total_transactions_sum))     
            st.header(f"GRAND TOTAL: ₹{total_sum}")

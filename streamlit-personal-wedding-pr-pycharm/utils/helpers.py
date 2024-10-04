def save_to_excel(df, file_path):
    """Save the DataFrame to an Excel file."""
    df.to_excel(file_path, index=False)

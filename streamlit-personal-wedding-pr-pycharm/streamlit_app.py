import streamlit as st
import pandas as pd
import os
import unidecode  # For normalizing characters
from utils.authentication import authenticate_user  # Import authentication function

# Main title of the app
st.title("Planificator de Nuntă")
st.subheader("Edi și Andri Nunta 2026")

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Function to display the login page
def show_login():
    st.subheader("Autentificare")
    username = st.text_input("Nume de utilizator")
    password = st.text_input("Parolă", type="password")
    login_button = st.button("Autentificare")

    if login_button:
        if authenticate_user(username, password):
            st.session_state["authenticated"] = True
            st.success("Autentificat cu succes!")
            return True  # Return True if authentication was successful
        else:
            st.error("Nume de utilizator sau parolă incorectă.")
    return False  # Return False if authentication was not successful


# Function to normalize Romanian characters
def normalize_string(s):
    return unidecode.unidecode(s) if isinstance(s, str) else s


# Function to display the main content
def show_main_content():
    st.sidebar.title("Navigare")
    page = st.sidebar.selectbox("Selectează pagina", ["Vizualizare invitați", "Editare invitați"])

    # Dynamic path to the Excel file
    file_path = os.path.join('data', 'invitati.xlsx')

    # Initialize df
    df = None

    # Check if the file exists
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        st.success("Fișierul a fost găsit și încărcat cu succes.")
        st.dataframe(df)  # Display the dataframe in the Streamlit app

        # Normalize the DataFrame
        df['Nume'] = df['Nume'].apply(normalize_string)
        df['Prenume'] = df['Prenume'].apply(normalize_string)
        df['Din partea'] = df['Din partea'].apply(normalize_string)

        # Create combined names for dropdown
        df['Combined'] = df.apply(lambda row: f"{row['Nume']} {row['Prenume']}", axis=1)

        if page == "Vizualizare invitați":
            st.subheader("Vizualizare invitați")

            # Filtering options
            name_filter = st.text_input("Filtru după Nume")
            surname_filter = st.text_input("Filtru după Prenume")

            # Dropdown for combined names with a default "Nimic selectat"
            combined_filter = st.selectbox("Filtru combinat (Nume Prenume)",
                                           ["Nimic selectat"] + df['Combined'].dropna().tolist())

            # Create filtered DataFrame
            filtered_df = df.copy()
            filtered_df = filtered_df.dropna(subset=['Nume', 'Prenume'])

            if name_filter:
                filtered_df = filtered_df[filtered_df['Nume'].str.contains(normalize_string(name_filter), case=False, na=False)]
            if surname_filter:
                filtered_df = filtered_df[filtered_df['Prenume'].str.contains(normalize_string(surname_filter), case=False, na=False)]
            if combined_filter != "Nimic selectat":
                selected_name, selected_surname = combined_filter.split(" ", 1)
                filtered_df = filtered_df[(filtered_df['Nume'].str.contains(selected_name, case=False, na=False)) &
                                           (filtered_df['Prenume'].str.contains(selected_surname, case=False, na=False))]

            st.dataframe(filtered_df)

            # Summary Statistics
            st.subheader("Trenduri și Sumarizări")
            total_guests = len(filtered_df)
            confirmed_guests = filtered_df[filtered_df['Confirmare prezenta nunta'] == True].count()['Confirmare prezenta nunta']
            uncertain_guests = filtered_df[filtered_df['Certitudine participare'] == 'Poate'].count()['Certitudine participare']

            st.write(f"**Total invitați:** {total_guests}")
            st.write(f"**Invitați confirmați:** {confirmed_guests}")
            st.write(f"**Invitați incerti:** {uncertain_guests}")

            # Distribution by certainty of participation
            participation_distribution = filtered_df['Certitudine participare'].value_counts()
            st.subheader("Distribuția Certitudinii Participării")
            st.bar_chart(participation_distribution)

            # Pie chart for menu selection
            menu_distribution = filtered_df['Meniu'].value_counts()
            st.subheader("Distribuția Meniului")
            st.bar_chart(menu_distribution)

            # Distribution of guests by sides
            side_distribution = filtered_df['Din partea'].value_counts()
            st.subheader("Distribuția Invitaților pe Părți")
            st.bar_chart(side_distribution)

            # Pivot table for participation certainty by side and menu count
            pivot_table = filtered_df.pivot_table(index='Din partea',
                                                   columns='Certitudine participare',
                                                   values='Meniu',
                                                   aggfunc='count',
                                                   fill_value=0)
            st.subheader("Pivot Table: Certitudine Participare per Parte")
            st.write(pivot_table)

        elif page == "Editare invitați":
            st.subheader("Editare invitați")
            # Dropdown for adding new guest
            st.header("Adaugă un nou invitat")
            with st.form("Add Guest"):
                new_name = st.text_input("Nume")
                new_surname = st.text_input("Prenume")
                new_menu = st.text_input("Meniu")
                new_certitude = st.selectbox("Certitudine participare", ['Da', 'Nu', 'Poate'])
                new_confirmation = st.checkbox("Confirmare prezență")

                add_guest = st.form_submit_button("Adaugă invitat")
                if add_guest:
                    new_row = {
                        "Nume": new_name,
                        "Prenume": new_surname,
                        "Meniu": new_menu,
                        "Certitudine participare": new_certitude,
                        "Confirmare prezenta nunta": new_confirmation
                    }
                    df = df.append(new_row, ignore_index=True)
                    df.to_excel(file_path, index=False)
                    st.success(f"Invitatul {new_name} {new_surname} a fost adăugat cu succes!")

            # Edit existing guest
            st.header("Editează un invitat existent")
            guest_names = df['Combined'].tolist()
            selected_guest = st.selectbox("Alege un invitat pentru editare", guest_names)

            if selected_guest:
                guest_row = df[df['Combined'] == selected_guest]
                if not guest_row.empty:
                    with st.form("Edit Guest"):
                        prenume = st.text_input('Prenume', guest_row['Prenume'].values[0])
                        certitudine_participare = st.selectbox('Certitudine participare', ['Da', 'Nu', 'Poate'], index=0)
                        meniu = st.text_input('Meniu', guest_row['Meniu'].values[0])
                        confirmare = st.checkbox('Confirmare prezență', guest_row['Confirmare prezenta nunta'].values[0])

                        submitted = st.form_submit_button("Salvează modificările")
                        if submitted:
                            # Update the DataFrame
                            df.loc[df['Combined'] == selected_guest, 'Prenume'] = prenume
                            df.loc[df['Combined'] == selected_guest, 'Certitudine participare'] = certitudine_participare
                            df.loc[df['Combined'] == selected_guest, 'Meniu'] = meniu
                            df.loc[df['Combined'] == selected_guest, 'Confirmare prezenta nunta'] = confirmare

                            # Save changes to Excel file
                            df.to_excel(file_path, index=False)
                            st.success(f"Datele pentru {guest_row['Combined'].values[0]} au fost actualizate!")

            # Delete existing guest
            st.header("Șterge un invitat existent")
            delete_guest = st.selectbox("Alege un invitat pentru ștergere", guest_names)

            if st.button("Șterge invitat"):
                df = df[df['Combined'] != delete_guest]
                df.to_excel(file_path, index=False)
                st.success(f"Invitatul {delete_guest} a fost șters cu succes!")
    else:
        st.error("Fișierul nu a fost găsit.")


# Main application logic
if not st.session_state.get("authenticated", False):  # Verifică dacă utilizatorul este autentificat
    if show_login():
        show_main_content()  # Afișează conținutul principal doar dacă utilizatorul s-a autentificat
else:
    show_main_content()  # Afișează direct conținutul principal dacă utilizatorul este deja autentificat

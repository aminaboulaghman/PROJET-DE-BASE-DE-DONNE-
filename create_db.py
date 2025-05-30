import streamlit as st
import sqlite3
import pandas as pd

st.write("Début du chargement de l'application")

# Connexion à la base
def get_conn():
    return sqlite3.connect('hotel.db', check_same_thread=False)

# Afficher les réservations
def afficher_reservations():
    conn = get_conn()
    df = pd.read_sql_query("""
        SELECT Reservation.id, date_debut, date_fin, Client.nom, Chambre.numero
        FROM Reservation
        JOIN Client ON Reservation.id_client = Client.id
        JOIN Chambre ON Reservation.id_chambre = Chambre.id
    """, conn)
    st.dataframe(df)

# Afficher les clients
def afficher_clients():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM Client", conn)
    st.dataframe(df)

# Chambres disponibles dans une période donnée
def chambres_disponibles(debut, fin):
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT * FROM Chambre
        WHERE id NOT IN (
            SELECT Chambre.id FROM Chambre
            JOIN Reservation ON Chambre.id = Reservation.id_chambre
            WHERE NOT (date_fin < '{debut}' OR date_debut > '{fin}')
        )
    """, conn)
    st.dataframe(df)

# Ajouter un client
def ajouter_client():
    st.subheader("Ajouter un nouveau client")
    with st.form("form_client"):
        id = st.number_input("ID", min_value=1, step=1)
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        cp = st.number_input("Code postal", step=1)
        email = st.text_input("Email")
        tel = st.text_input("Téléphone")
        nom = st.text_input("Nom complet")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            conn = get_conn()
            conn.execute("INSERT INTO Client VALUES (?, ?, ?, ?, ?, ?, ?)",
                         (id, adresse, ville, cp, email, tel, nom))
            conn.commit()
            st.success("Client ajouté.")
            afficher_clients()

# Ajouter une réservation
def ajouter_reservation():
    st.subheader("Ajouter une réservation")
    with st.form("form_reservation"):
        id = st.number_input("ID", min_value=1, step=1)
        id_client = st.number_input("ID Client", min_value=1, step=1)
        id_chambre = st.number_input("ID Chambre", min_value=1, step=1)
        date_debut = st.date_input("Date de début")
        date_fin = st.date_input("Date de fin")
        submitted = st.form_submit_button("Réserver")
        if submitted:
            conn = get_conn()
            conn.execute("INSERT INTO Reservation VALUES (?, ?, ?, ?, ?)",
                         (id, id_client, id_chambre, str(date_debut), str(date_fin)))
            conn.commit()
            st.success("Réservation ajoutée.")
            afficher_reservations()

# Interface principale
st.title("🏨 Gestion Hôtelière")
choix = st.sidebar.radio("Menu", [
    "📋 Liste des réservations",
    "👤 Liste des clients",
    "🔍 Chambres disponibles",
    "➕ Ajouter un client",
    "🛎️ Ajouter une réservation"
])

if choix == "📋 Liste des réservations":
    afficher_reservations()
elif choix == "👤 Liste des clients":
    afficher_clients()
elif choix == "🔍 Chambres disponibles":
    d1 = st.date_input("Date de début")
    d2 = st.date_input("Date de fin")
    if d1 and d2:
        chambres_disponibles(str(d1), str(d2))
elif choix == "➕ Ajouter un client":
    ajouter_client()
elif choix == "🛎️ Ajouter une réservation":
    ajouter_reservation()

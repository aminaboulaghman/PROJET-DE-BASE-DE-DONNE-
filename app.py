import streamlit as st
import sqlite3
import pandas as pd
import os



def get_conn():
    return sqlite3.connect('hotel.db', check_same_thread=False)

def create_tables():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Client (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adresse TEXT,
        ville TEXT,
        code_postal TEXT,
        email TEXT,
        telephone TEXT,
        nom TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Chambre (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_hotel INTEGER,
        numero TEXT,
        type TEXT,
        prix REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_client INTEGER,
        id_chambre INTEGER,
        date_debut TEXT,
        date_fin TEXT,
        FOREIGN KEY (id_client) REFERENCES Client(id),
        FOREIGN KEY (id_chambre) REFERENCES Chambre(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Hotel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        ville TEXT,
        nb_etoiles INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# Afficher les réservations
def afficher_reservations():
    conn = get_conn()
    try:
        df = pd.read_sql_query("""
            SELECT Reservation.id, date_debut, date_fin, Client.nom 
            FROM Reservation
            JOIN Client ON Reservation.id_client = Client.id
        """, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des réservations : {e}")

# Afficher les clients
def afficher_clients():
    conn = get_conn()
    try:
        df = pd.read_sql_query("SELECT * FROM Client", conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des clients : {e}")

# Chambres disponibles dans une période donnée
def chambres_disponibles(debut, fin):
    conn = get_conn()
    try:
        query = f"""
            SELECT * FROM Chambre
            WHERE id NOT IN (
                SELECT id_chambre FROM Reservation
                WHERE NOT (date_fin < '{debut}' OR date_debut > '{fin}')
            )
        """
        df = pd.read_sql_query(query, conn)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des chambres disponibles : {e}")

# Ajouter un client
def ajouter_client():
    st.subheader("Ajouter un nouveau client")
    with st.form("form_client"):
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        cp = st.text_input("Code postal")
        email = st.text_input("Email")
        tel = st.text_input("Téléphone")
        nom = st.text_input("Nom complet")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            try:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO Client (adresse, ville, code_postal, email, telephone, nom)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (adresse, ville, cp, email, tel, nom))
                conn.commit()
                st.success("Client ajouté.")
            except Exception as e:
                st.error(f"Erreur lors de l'ajout du client : {e}")

# Ajouter une réservation
def ajouter_reservation():
    st.subheader("Ajouter une réservation")
    with st.form("form_reservation"):
        date_debut = st.date_input("Date de début")
        date_fin = st.date_input("Date de fin")
        id_client = st.number_input("ID Client", min_value=1, step=1)
        id_chambre = st.number_input("ID Chambre", min_value=1, step=1)
        submitted = st.form_submit_button("Réserver")
        if submitted:
            try:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO Reservation (id_client, id_chambre, date_debut, date_fin)
                    VALUES (?, ?, ?, ?)
                """, (id_client, id_chambre, str(date_debut), str(date_fin)))
                conn.commit()
                st.success("Réservation ajoutée.")
            except Exception as e:
                st.error(f"Erreur lors de l'ajout de la réservation : {e}")

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

import mysql.connector
import tkinter as tk
from tkinter import messagebox
import uuid  # Pour générer des identifiants uniques


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Remplacez par votre nom d'utilisateur MySQL
            password="azerty123",  # Remplacez par votre mot de passe MySQL
            database="gestion_entrepot"
        )
        self.cursor = self.conn.cursor()

    def ajouter_produit(self, nom, quantite):
        sql = "INSERT INTO produits (nom, quantite) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, quantite))
        self.conn.commit()

    def afficher_produits(self):
        self.cursor.execute("SELECT * FROM produits")
        return self.cursor.fetchall()

    def ajouter_client(self, nom, adresse):
        sql = "INSERT INTO clients (nom, adresse) VALUES (%s, %s)"
        self.cursor.execute(sql, (nom, adresse))
        self.conn.commit()
        return self.cursor.lastrowid  # Retourne l'identifiant du client ajouté

    def afficher_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def supprimer_client(self, identifiant):
        sql = "DELETE FROM clients WHERE id = %s"  # Suppression par identifiant
        self.cursor.execute(sql, (identifiant,))
        self.conn.commit()

    def ajouter_commande(self, client_id, produit, quantite):
        sql = "INSERT INTO commandes (client_id, produit, quantite) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (client_id, produit, quantite))
        self.conn.commit()

    def afficher_commandes(self):
        self.cursor.execute("SELECT * FROM commandes")
        return self.cursor.fetchall()

    def modifier_stock(self, nom_produit, nouvelle_quantite):
        sql = "UPDATE produits SET quantite = %s WHERE nom = %s"
        self.cursor.execute(sql, (nouvelle_quantite, nom_produit))
        self.conn.commit()

    def get_quantite_produit(self, nom_produit):
        self.cursor.execute("SELECT quantite FROM produits WHERE nom = %s", (nom_produit,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def close(self):
        self.cursor.close()
        self.conn.close()


class Produit:
    def __init__(self, nom, quantite):
        self.nom = nom
        self.quantite = quantite

    def afficher_details(self):
        return f"Produit : {self.nom}, Quantité en stock : {self.quantite}"


class Client:
    def __init__(self, nom, adresse):
        self.nom = nom
        self.adresse = adresse
        self.id = None  # L'identifiant sera défini lors de l'ajout à la base de données

    def afficher_details(self):
        return f"Client ID : {self.id}, Nom : {self.nom}, Adresse : {self.adresse}"


class Commande:
    def __init__(self, client_id, produit, quantite):
        self.client_id = client_id
        self.produit = produit
        self.quantite = quantite

    def afficher_details(self):
        return f"Commande - Client ID : {self.client_id}, Produit : {self.produit}, Quantité : {self.quantite}"


class Entrepot:
    def __init__(self, db):
        self.db = db

    def ajouter_produit(self, produit):
        self.db.ajouter_produit(produit.nom, produit.quantite)

    def verifier_stock(self, nom_produit, quantite_demandee):
        quantite_disponible = self.db.get_quantite_produit(nom_produit)
        return quantite_disponible >= quantite_demandee

    def modifier_stock(self, nom_produit, nouvelle_quantite):
        self.db.modifier_stock(nom_produit, nouvelle_quantite)


class GestionnaireClients:
    def __init__(self, entrepot, db):
        self.clients = []
        self.entrepot = entrepot
        self.db = db

    def ajouter_client(self, client):
        client_id = self.db.ajouter_client(client.nom, client.adresse)
        client.id = identifiant = str(uuid.uuid4())  # Assigner l'identifiant au client
        self.clients.append(client)
        return f"Client '{client.nom}' ajouté avec succès."

    def supprimer_client(self, identifiant):
        self.db.supprimer_client(identifiant)
        # Supprime également le client de la liste
        self.clients = [client for client in self.clients if client.id != identifiant]

    def passer_commande(self, client_id, produit, quantite):
        # Vérifiez d'abord si le client existe
        self.db.cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client_existe = self.db.cursor.fetchone()
        
        if not client_existe:
            return f"Client ID '{client_id}' n'existe pas."  # Message d'erreur si le client n'existe pas
        
        # Vérifiez la disponibilité du produit
        if self.entrepot.verifier_stock(produit, quantite):
            try:
                self.db.ajouter_commande(client_id, produit, quantite)
                quantite_disponible = self.db.get_quantite_produit(produit)
                nouvelle_quantite = quantite_disponible - quantite
                self.entrepot.modifier_stock(produit, nouvelle_quantite)
                return f"Commande pour le client ID {client_id} passée avec succès."
            except Exception as e:
                return f"Erreur lors de la commande : {str(e)}"
        
        return f"Stock insuffisant pour la commande du client ID {client_id}."



class App:
    def __init__(self, root, db):
        self.root = root
        self.root.title("Gestion d'Entrepôt")
        self.root.geometry("800x600")
        self.root.config(bg="#e8f0fe")

        self.entrepot = Entrepot(db)  # Stock vide au départ
        self.gestionnaire = GestionnaireClients(self.entrepot, db)

        # Interface utilisateur
        self.create_widgets()

    def create_widgets(self):
        # Frame pour ajouter un produit
        frame_produit = tk.Frame(self.root, bg="#e8f0fe")
        frame_produit.pack(pady=10)

        tk.Label(frame_produit, text="Nom du produit", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.nom_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.nom_produit_entry.grid(row=0, column=1)

        tk.Label(frame_produit, text="Quantité", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.quantite_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.quantite_produit_entry.grid(row=1, column=1)

        tk.Button(frame_produit, text="Ajouter Produit", command=self.ajouter_produit, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, pady=10, columnspan=2)

        # Frame pour ajouter un client
        frame_client = tk.Frame(self.root, bg="#e8f0fe")
        frame_client.pack(pady=10)

        tk.Label(frame_client, text="Nom du client", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.nom_client_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.nom_client_entry.grid(row=0, column=1)

        tk.Label(frame_client, text="Adresse", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.adresse_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.adresse_entry.grid(row=1, column=1)

        tk.Button(frame_client, text="Ajouter Client", command=self.ajouter_client, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, pady=10, columnspan=2)

        tk.Button(frame_client, text="Supprimer Client", command=self.supprimer_client, bg="#f44336", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=10, columnspan=2)

        # Frame pour passer une commande
        frame_commande = tk.Frame(self.root, bg="#e8f0fe")
        frame_commande.pack(pady=10)

        tk.Label(frame_commande, text="Client ID", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.client_id_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.client_id_entry.grid(row=0, column=1)

        tk.Label(frame_commande, text="Produit", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.produit_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.produit_entry.grid(row=1, column=1)

        tk.Label(frame_commande, text="Quantité", bg="#e8f0fe", font=("Helvetica", 12)).grid(row=2, column=0, padx=5, pady=5)
        self.quantite_commande_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.quantite_commande_entry.grid(row=2, column=1)

        tk.Button(frame_commande, text="Passer Commande", command=self.passer_commande, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=10, columnspan=2)

        # Boutons pour afficher les produits et les clients
        tk.Button(self.root, text="Afficher Produits", command=self.afficher_produits, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)
        tk.Button(self.root, text="Afficher Clients", command=self.afficher_clients, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)
        tk.Button(self.root, text="Afficher Commandes", command=self.afficher_commandes, bg="#2196F3", fg="white", font=("Helvetica", 12)).pack(pady=5)

        # Affichage des résultats
        self.resultat_text = tk.Text(self.root, height=10, width=80, font=("Helvetica", 12))
        self.resultat_text.pack(pady=10)

    def afficher_produits(self):
        produits = self.entrepot.db.afficher_produits()
        self.resultat_text.delete(1.0, tk.END)  # Effacer le texte précédent
        for produit in produits:
            self.resultat_text.insert(tk.END, f"ID: {produit[0]}, Nom: {produit[1]}, Quantité: {produit[2]}\n")

    def afficher_clients(self):
        clients = self.entrepot.db.afficher_clients()
        self.resultat_text.delete(1.0, tk.END)  # Effacer le texte précédent
        for client in clients:
            self.resultat_text.insert(tk.END, f"ID: {client[0]}, Nom: {client[1]}, Adresse: {client[2]}\n")

    def afficher_commandes(self):
        produits = self.entrepot.db.afficher_commandes()
        self.resultat_text.delete(1.0, tk.END)  # Effacer le texte précédent
        for produit in produits:
            self.resultat_text.insert(tk.END, f"ID: {produit[0]}, Quantité: {produit[1]}, Nom: {produit[2]}\n")

    def ajouter_produit(self):
        nom = self.nom_produit_entry.get()
        quantite = self.quantite_produit_entry.get()

        if nom and quantite.isdigit():
            produit = Produit(nom, int(quantite))
            self.entrepot.ajouter_produit(produit)
            self.nom_produit_entry.delete(0, tk.END)
            self.quantite_produit_entry.delete(0, tk.END)
            messagebox.showinfo("Succès", f"Produit '{nom}' ajouté avec succès!")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer des informations valides pour le produit.")

    def ajouter_client(self):
        nom = self.nom_client_entry.get()
        adresse = self.adresse_entry.get()
        if nom and adresse:
            client = Client(nom, adresse)
            message = self.gestionnaire.ajouter_client(client)
            self.resultat_text.insert(tk.END, message + "\n")
            self.nom_client_entry.delete(0, tk.END)
            self.adresse_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez entrer des informations valides pour le client.")

    def supprimer_client(self):
        client_id = self.client_id_entry.get()
        if client_id.isdigit():
            self.gestionnaire.supprimer_client(int(client_id))
            messagebox.showinfo("Succès", f"Client {client_id} supprimé avec succès!")
            self.client_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un identifiant valide.")

    def passer_commande(self):
        client_id = self.client_id_entry.get()
        produit = self.produit_entry.get()
        quantite = self.quantite_commande_entry.get()

        if client_id.isdigit() and produit and quantite.isdigit():
            message = self.gestionnaire.passer_commande(int(client_id), produit, int(quantite))
            self.resultat_text.insert(tk.END, message + "\n")
            self.produit_entry.delete(0, tk.END)
            self.quantite_commande_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez entrer des informations valides pour la commande.")


if __name__ == "__main__":
    db = Database()
    app = App(tk.Tk(), db)
    app.root.mainloop()
    db.close()

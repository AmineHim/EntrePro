import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk


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

    def afficher_clients(self):
        self.cursor.execute("SELECT * FROM clients")
        return self.cursor.fetchall()

    def supprimer_client(self, identifiant):
        sql = "DELETE FROM clients WHERE id = %s"  # Suppression par identifiant
        self.cursor.execute(sql, (identifiant,))
        self.conn.commit()

    def restaurer(self):
        try:
            self.cursor.execute("DROP TABLE IF EXISTS commandes")
            self.cursor.execute("DROP TABLE IF EXISTS clients")
            self.cursor.execute("DROP TABLE IF EXISTS produits")
            messagebox.showinfo("Restaurer", "Tables supprimées avec succès.")
            self.create_table()
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la restauration : {str(e)}")
        self.conn.commit()

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    quantite INT NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    adresse VARCHAR(255) NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_id INT NOT NULL,
                    produit VARCHAR(255) NOT NULL,
                    quantite INT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            """)
            messagebox.showinfo("Tables Créées", "Tables créées avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la création des tables : {str(e)}")
        self.conn.commit()

    def ajouter_commande(self, client_id, produit, quantite):
        # Vérifier la quantité disponible dans le stock
        stock_quantite = self.get_quantite_produit(produit)
        if stock_quantite >= quantite:
            sql = "INSERT INTO commandes (client_id, produit, quantite) VALUES (%s, %s, %s)"
            self.cursor.execute(sql, (client_id, produit, quantite))
            self.decrease_product_stock(produit, quantite)  # Déduire la quantité du stock
            self.conn.commit()
            return True
        else:
            return False  # Pas assez de stock

    def decrease_product_stock(self, produit, quantite):
        sql = "UPDATE produits SET quantite = quantite - %s WHERE nom = %s"
        self.cursor.execute(sql, (quantite, produit))
        self.conn.commit()

    def afficher_commandes(self):
        self.cursor.execute("SELECT * FROM commandes")
        return self.cursor.fetchall()

    def get_quantite_produit(self, nom_produit):
        self.cursor.execute("SELECT quantite FROM produits WHERE nom = %s", (nom_produit,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def get_client_nom(self, client_id):
        self.cursor.execute("SELECT nom FROM clients WHERE id = %s", (client_id,))
        result = self.cursor.fetchone()
        return result[0] if result else "Inconnu"

    def close(self):
        self.cursor.close()
        self.conn.close()


class App:
    def __init__(self, root, db):
        self.root = root
        self.root.title("Gestion d'Entrepôt")
        self.root.geometry("800x600")
        
        self.db = db

        # Création d'un Notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Onglet Produits
        self.tab_produits = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_produits, text="Produits")

        # Onglet Clients
        self.tab_clients = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_clients, text="Clients")

        # Onglet Commandes
        self.tab_commandes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_commandes, text="Commandes")

        # Onglet Restaurer
        self.tab_restaurer = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_restaurer, text="Restaurer")

        # Widgets pour l'onglet Produits
        self.create_product_widgets()

        # Widgets pour l'onglet Clients
        self.create_client_widgets()

        # Widgets pour l'onglet Commandes
        self.create_order_widgets()

        # Widgets pour l'onglet Restaurer
        self.create_restor_widgets()

    def create_product_widgets(self):
        frame_produit = ttk.Frame(self.tab_produits)
        frame_produit.pack(pady=10)

        tk.Label(frame_produit, text="Nom du produit", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.nom_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.nom_produit_entry.grid(row=0, column=1)

        tk.Label(frame_produit, text="Quantité", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.quantite_produit_entry = tk.Entry(frame_produit, font=("Helvetica", 12), width=30)
        self.quantite_produit_entry.grid(row=1, column=1)

        tk.Button(frame_produit, text="Ajouter Produit", command=self.ajouter_produit, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, pady=10, columnspan=2)
        tk.Button(frame_produit, text="Afficher Produits", command=self.afficher_produits, bg="#2196F3", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, pady=5, columnspan=2)

    def create_client_widgets(self):
        frame_client = ttk.Frame(self.tab_clients)
        frame_client.pack(pady=10)

        tk.Label(frame_client, text="Nom du client", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.nom_client_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.nom_client_entry.grid(row=0, column=1)

        tk.Label(frame_client, text="Adresse", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.adresse_entry = tk.Entry(frame_client, font=("Helvetica", 12), width=30)
        self.adresse_entry.grid(row=1, column=1)

        tk.Button(frame_client, text="Ajouter Client", command=self.ajouter_client, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=2, column=0, pady=10, columnspan=2)
        tk.Button(frame_client, text="Supprimer Client", command=self.supprimer_client, bg="#F44336", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=5, columnspan=2)
        tk.Button(frame_client, text="Afficher Clients", command=self.afficher_clients, bg="#2196F3", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, pady=5, columnspan=2)

    def create_order_widgets(self):
        frame_commande = ttk.Frame(self.tab_commandes)
        frame_commande.pack(pady=10)

        tk.Label(frame_commande, text="Client ID", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)
        self.client_id_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.client_id_entry.grid(row=0, column=1)

        tk.Label(frame_commande, text="Produit", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)
        self.produit_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.produit_entry.grid(row=1, column=1)

        tk.Label(frame_commande, text="Quantité", font=("Helvetica", 12)).grid(row=2, column=0, padx=5, pady=5)
        self.quantite_commande_entry = tk.Entry(frame_commande, font=("Helvetica", 12), width=30)
        self.quantite_commande_entry.grid(row=2, column=1)

        tk.Button(frame_commande, text="Ajouter Commande", command=self.ajouter_commande, bg="#4CAF50", fg="white", font=("Helvetica", 12)).grid(row=3, column=0, pady=10, columnspan=2)
        tk.Button(frame_commande, text="Afficher Commandes", command=self.afficher_commandes, bg="#2196F3", fg="white", font=("Helvetica", 12)).grid(row=4, column=0, pady=5, columnspan=2)

    def create_restor_widgets(self):
        frame_restaurer = ttk.Frame(self.tab_restaurer)
        frame_restaurer.pack(pady=10)

        tk.Button(frame_restaurer, text="Restaurer Tables", command=self.restaurer_tables, bg="#F44336", fg="white", font=("Helvetica", 12)).grid(row=0, column=0, pady=10, columnspan=2)

    def restaurer_tables(self):
        self.db.restaurer()

    def ajouter_produit(self):
        nom = self.nom_produit_entry.get()
        quantite = self.quantite_produit_entry.get()
        if nom and quantite:
            try:
                quantite = int(quantite)
                self.db.ajouter_produit(nom, quantite)
                messagebox.showinfo("Succès", "Produit ajouté avec succès.")
                self.nom_produit_entry.delete(0, tk.END)
                self.quantite_produit_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Erreur", "La quantité doit être un nombre entier.")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")

    def afficher_produits(self):
        produits = self.db.afficher_produits()
        produits_str = "\n".join([f"ID: {p[0]}, Nom: {p[1]}, Quantité: {p[2]}" for p in produits])
        messagebox.showinfo("Produits", produits_str if produits else "Aucun produit trouvé.")

    def ajouter_client(self):
        nom = self.nom_client_entry.get()
        adresse = self.adresse_entry.get()
        if nom and adresse:
            self.db.ajouter_client(nom, adresse)
            messagebox.showinfo("Succès", "Client ajouté avec succès.")
            self.nom_client_entry.delete(0, tk.END)
            self.adresse_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")

    def supprimer_client(self):
        nom_client = self.nom_client_entry.get()  # Utiliser le nom du client pour rechercher l'ID
        if nom_client:
            client_id = self.get_client_id(nom_client)  # Obtenez l'ID du client à partir du nom
            if client_id:
                self.db.supprimer_client(client_id)  # Supprimer le client en utilisant son ID
                messagebox.showinfo("Succès", "Client supprimé avec succès.")
                self.nom_client_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Erreur", "Client introuvable.")
        else:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de client valide.")

    def get_client_id(self, nom_client):
        self.db.cursor.execute("SELECT id FROM clients WHERE nom = %s", (nom_client,))
        result = self.db.cursor.fetchone()
        return result[0] if result else None  # Retourne l'ID du client ou None si non trouvé

    def afficher_clients(self):
        clients = self.db.afficher_clients()
        clients_str = "\n".join([f"ID: {c[0]}, Nom: {c[1]}, Adresse: {c[2]}" for c in clients])
        messagebox.showinfo("Clients", clients_str if clients else "Aucun client trouvé.")

    def ajouter_commande(self):
        client_id = self.client_id_entry.get()
        produit = self.produit_entry.get()
        quantite = self.quantite_commande_entry.get()
        if client_id and produit and quantite:
            try:
                client_id = int(client_id)
                quantite = int(quantite)
                if self.db.ajouter_commande(client_id, produit, quantite):
                    messagebox.showinfo("Succès", "Commande ajoutée avec succès.")
                    self.client_id_entry.delete(0, tk.END)
                    self.produit_entry.delete(0, tk.END)
                    self.quantite_commande_entry.delete(0, tk.END)
                else:
                    messagebox.showerror("Erreur", "Quantité insuffisante en stock.")
            except ValueError:
                messagebox.showerror("Erreur", "L'ID du client et la quantité doivent être des nombres entiers.")
        else:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")

    def afficher_commandes(self):
        commandes = self.db.afficher_commandes()
        commandes_str = "\n".join([f"ID: {c[0]}, Client ID: {c[1]}, Produit: {c[2]}, Quantité: {c[3]}" for c in commandes])
        messagebox.showinfo("Commandes", commandes_str if commandes else "Aucune commande trouvée.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    db = Database()
    app = App(tk.Tk(), db)
    db.create_table()  # Création des tables au démarrage
    app.run()
    db.close()  # Fermer la connexion à la base de données à la fin

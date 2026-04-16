"""Script pour injecter les utilisateurs de test"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='', database='futurekawa')
cursor = conn.cursor()

# Supprime et recrée les utilisateurs
cursor.execute('DELETE FROM utilisateurs')

users = [
    ('Dupont', 'Jean', 'jean@kawa.com', 'hash123', 1, 2),
    ('Silva', 'Maria', 'maria@kawa.com', 'hash123', 1, 1),
    ('Garcia', 'Carlos', 'carlos@kawa.com', 'hash123', 7, 2),
    ('Mendoza', 'Elena', 'elena@kawa.com', 'hash123', 13, 2),
    ('Lopez', 'Juan', 'juan@kawa.com', 'hash123', 2, 1),
]

for user in users:
    cursor.execute('''
        INSERT INTO utilisateurs (nom, prenom, mail, mdp, idExploitation, idPoste)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', user)

conn.commit()

# Vérifie
cursor.execute('SELECT COUNT(*) FROM utilisateurs')
count = cursor.fetchone()[0]
print(f'[OK] {count} utilisateurs insérés')

cursor.execute('SELECT nom, prenom, mail FROM utilisateurs')
for row in cursor.fetchall():
    print(f'  - {row[0]} {row[1]}: {row[2]}')

conn.close()
print('[OK] Données prêtes pour test!')

"""Script pour peupler les tables de référence (dog_breeds et consultation_reasons)"""
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Dog breeds data to seed
DOG_BREEDS = [
    'Labrador Retriever',
    'Golden Retriever',
    'Berger Allemand',
    'Bulldog Français',
    'Berger Belge Malinois',
    'Border Collie',
    'Rottweiler',
    'Yorkshire Terrier',
    'Chihuahua',
    'Jack Russell Terrier',
    'Cocker Spaniel',
    'Boxer',
    'Husky Sibérien',
    'Beagle',
    'Cavalier King Charles',
    'Caniche',
    'Shih Tzu',
    'Bichon Frisé',
    'Dogue de Bordeaux',
    'Berger Australien',
    'Épagneul Breton',
    'Setter Anglais',
    'Pointer',
    'Braque de Weimar',
    'Doberman',
    'Dogue Allemand',
    'Saint-Bernard',
    'Terre-Neuve',
    'Bouvier Bernois',
    'Akita Inu',
    'Shiba Inu',
    'Basenji',
    'Whippet',
    'Lévrier',
    'Mastiff',
    'Bull Terrier',
    'Staffordshire Bull Terrier',
    'Carlin',
    'Boston Terrier',
    'Schnauzer',
    'Teckel',
    'Spitz',
    'Chow Chow',
    'Shar Pei',
    'Croisé/Bâtard',
    'Autre'
]

# Consultation reasons data to seed
CONSULTATION_REASONS = [
    'Tremblements et/ou incoordination des mouvements',
    'Convulsion et/ou comportement compulsif',
    'Troubles locomoteurs (trouble de la motricité comme parésie ou paralysie)',
    'Trouble de l\'équilibre (ataxie)',
    'Atteinte vestibulaire (tête penchée)',
    'Déficit des nerfs crâniens (hors atteinte vestibulaire)'
]


def seed_database():
    """Peuple les tables dog_breeds et consultation_reasons"""
    # Get database URL from environment and convert to sync driver
    database_url = os.getenv("DATABASE_URL", "mysql+aiomysql://neuro_user:NeuroVet2024!@localhost:3306/neurolocalizer")
    # Convert async driver to sync driver for SQLAlchemy
    database_url = database_url.replace("mysql+aiomysql://", "mysql+pymysql://")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        # Check if dog breeds data exists
        breed_count = conn.execute(text("SELECT COUNT(*) FROM dog_breeds")).scalar()

        if breed_count == 0:
            print("Insertion des races de chiens...")
            for breed in DOG_BREEDS:
                conn.execute(
                    text("INSERT INTO dog_breeds (name, created_at) VALUES (:name, :created_at)"),
                    {"name": breed, "created_at": datetime.utcnow()}
                )
            print(f"✓ {len(DOG_BREEDS)} races de chiens insérées")
        else:
            print(f"Les races de chiens existent déjà ({breed_count} entrées)")

        # Check if consultation reasons data exists
        reason_count = conn.execute(text("SELECT COUNT(*) FROM consultation_reasons")).scalar()

        if reason_count == 0:
            print("Insertion des raisons de consultation...")
            for reason in CONSULTATION_REASONS:
                conn.execute(
                    text("INSERT INTO consultation_reasons (name, created_at) VALUES (:name, :created_at)"),
                    {"name": reason, "created_at": datetime.utcnow()}
                )
            print(f"✓ {len(CONSULTATION_REASONS)} raisons de consultation insérées")
        else:
            print(f"Les raisons de consultation existent déjà ({reason_count} entrées)")

        conn.commit()
        print("\n✓ Base de données peuplée avec succès!")


if __name__ == "__main__":
    seed_database()

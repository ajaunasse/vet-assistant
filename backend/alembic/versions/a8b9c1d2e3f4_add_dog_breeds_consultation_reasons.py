"""add dog breeds and consultation reasons tables

Revision ID: a8b9c1d2e3f4
Revises: 50c5da35f496
Create Date: 2025-01-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'a8b9c1d2e3f4'
down_revision = '50c5da35f496'
branch_labels = None
depends_on = None

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


def upgrade() -> None:
    # Get bind for direct SQL execution
    bind = op.get_bind()
    
    # Check if dog_breeds table exists
    result = bind.execute(sa.text("SHOW TABLES LIKE 'dog_breeds'")).fetchone()
    if not result:
        # Create dog_breeds table
        op.create_table(
            'dog_breeds',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(100), nullable=False, unique=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )

    # Check if consultation_reasons table exists
    result = bind.execute(sa.text("SHOW TABLES LIKE 'consultation_reasons'")).fetchone()
    if not result:
        # Create consultation_reasons table
        op.create_table(
            'consultation_reasons',
            sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
            sa.Column('name', sa.String(255), nullable=False, unique=True),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            mysql_engine='InnoDB',
            mysql_charset='utf8mb4'
        )

    # Check if dog breeds data exists
    breed_count = bind.execute(sa.text("SELECT COUNT(*) FROM dog_breeds")).scalar()
    if breed_count == 0:
        # Seed dog breeds data
        dog_breeds_table = sa.table(
            'dog_breeds',
            sa.column('name', sa.String),
            sa.column('created_at', sa.DateTime)
        )
        
        current_time = datetime.utcnow()
        breed_data = [
            {'name': breed, 'created_at': current_time}
            for breed in DOG_BREEDS
        ]
        
        op.bulk_insert(dog_breeds_table, breed_data)

    # Check if consultation reasons data exists
    reason_count = bind.execute(sa.text("SELECT COUNT(*) FROM consultation_reasons")).scalar()
    if reason_count == 0:
        # Seed consultation reasons data
        consultation_reasons_table = sa.table(
            'consultation_reasons',
            sa.column('name', sa.String),
            sa.column('description', sa.Text),
            sa.column('created_at', sa.DateTime)
        )
        
        current_time = datetime.utcnow()
        reason_data = [
            {'name': reason, 'description': None, 'created_at': current_time}
            for reason in CONSULTATION_REASONS
        ]
        
        op.bulk_insert(consultation_reasons_table, reason_data)


def downgrade() -> None:
    op.drop_table('consultation_reasons')
    op.drop_table('dog_breeds')
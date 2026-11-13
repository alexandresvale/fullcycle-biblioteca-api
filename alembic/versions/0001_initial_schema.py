"""create initial tables books readers loans

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-11-13 08:16:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())

    if not inspector.has_table("books"):
        op.create_table(
            "books",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("author", sa.String(length=150), nullable=False),
            sa.Column("isbn", sa.String(length=20), nullable=False),
            sa.Column("total_copies", sa.Integer(), nullable=False),
            sa.Column("available_copies", sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)

    if not inspector.has_table("readers"):
        op.create_table(
            "readers",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("name", sa.String(length=150), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("document", sa.String(length=30), nullable=False),
            sa.Column("category", sa.String(length=20), nullable=False),
            sa.Column("active", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_readers_document", "readers", ["document"], unique=True)
        op.create_index("ix_readers_email", "readers", ["email"], unique=True)

    if not inspector.has_table("loans"):
        op.create_table(
            "loans",
            sa.Column("id", sa.Uuid(), nullable=False),
            sa.Column("book_id", sa.Uuid(), nullable=False),
            sa.Column("reader_id", sa.Uuid(), nullable=False),
            sa.Column("borrowed_at", sa.Date(), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=False),
            sa.Column("returned_at", sa.Date(), nullable=True),
            sa.Column("fine_amount", sa.Numeric(precision=10, scale=2), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_loans_book_id", "loans", ["book_id"], unique=False)
        op.create_index("ix_loans_reader_id", "loans", ["reader_id"], unique=False)
        op.create_index("ix_loans_status", "loans", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_loans_status", table_name="loans")
    op.drop_index("ix_loans_reader_id", table_name="loans")
    op.drop_index("ix_loans_book_id", table_name="loans")
    op.drop_table("loans")

    op.drop_index("ix_readers_email", table_name="readers")
    op.drop_index("ix_readers_document", table_name="readers")
    op.drop_table("readers")

    op.drop_index("ix_books_isbn", table_name="books")
    op.drop_table("books")

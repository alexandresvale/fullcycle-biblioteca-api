import pytest

from src.core.exceptions import DomainError
from src.modules.readers.domain.entities import Reader, ReaderCategory
from src.modules.readers.domain.exceptions import InactiveReaderError


def test_reader_normalizes_fields_and_defaults_to_active_standard() -> None:
    reader = Reader(
        name="  Ricardo Vale  ",
        email="  Ricardo.Vale@Example.COM ",
        document="123.456.789-00",
    )

    assert reader.name == "Ricardo Vale"
    assert reader.email == "ricardo.vale@example.com"
    assert reader.document == "12345678900"
    assert reader.category == ReaderCategory.STANDARD
    assert reader.active is True
    reader.ensure_active()


def test_reader_deactivate_and_activate() -> None:
    reader = Reader(
        name="Alexandre Vale",
        email="alexandre@example.com",
        document="MAT-2026-01",
        category=ReaderCategory.ACADEMIC,
    )

    reader.deactivate()
    assert reader.active is False

    with pytest.raises(InactiveReaderError):
        reader.ensure_active()

    reader.activate()
    assert reader.active is True
    reader.ensure_active()


@pytest.mark.parametrize(
    ("name", "email", "document"),
    [
        ("Al", "valid@example.com", "12345678900"),
        ("A" * 151, "valid@example.com", "12345678900"),
        ("Valid Name", "invalid-email", "12345678900"),
        ("Valid Name", "valid@example.com", "12"),
    ],
)
def test_reader_invariants_raise_domain_error(name: str, email: str, document: str) -> None:
    with pytest.raises(DomainError):
        Reader(name=name, email=email, document=document)

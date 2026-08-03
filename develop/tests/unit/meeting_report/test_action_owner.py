import pytest

from models.meeting_report import ActionOwner


def test_action_owner_serializes() -> None:
    owner = ActionOwner(
        display_name="Equipo Oracle",
    )

    assert owner.as_dict() == {
        "display_name": "Equipo Oracle",
    }


def test_action_owner_normalizes_display_name() -> None:
    owner = ActionOwner(
        display_name=" Infraestructura ",
    )

    assert (
        owner.display_name
        == "Infraestructura"
    )


def test_action_owner_behaves_as_readable_value() -> None:
    owner = ActionOwner(
        display_name="Remy",
    )

    assert str(owner) == "Remy"


def test_action_owner_from_value_accepts_string() -> None:
    owner = ActionOwner.from_value(
        " DBA "
    )

    assert isinstance(
        owner,
        ActionOwner,
    )

    assert owner.display_name == "DBA"


def test_action_owner_from_value_accepts_existing_owner() -> None:
    original_owner = ActionOwner(
        display_name="Equipo Oracle",
    )

    result = ActionOwner.from_value(
        original_owner
    )

    assert result is original_owner


def test_action_owner_rejects_empty_display_name() -> None:
    with pytest.raises(
        ValueError,
        match="display_name no puede estar vacío",
    ):
        ActionOwner(
            display_name="   ",
        )


def test_action_owner_from_value_rejects_non_string() -> None:
    with pytest.raises(
        TypeError,
        match="requiere una cadena",
    ):
        ActionOwner.from_value(
            123
        )


def test_action_owner_supports_person_team_and_area() -> None:
    owners = [
        ActionOwner(
            display_name="Remy",
        ),
        ActionOwner(
            display_name="Equipo Oracle",
        ),
        ActionOwner(
            display_name="Infraestructura",
        ),
    ]

    assert [
        owner.display_name
        for owner in owners
    ] == [
        "Remy",
        "Equipo Oracle",
        "Infraestructura",
    ]


def test_action_owner_equality_is_value_based() -> None:
    first_owner = ActionOwner(
        display_name="DBA",
    )

    second_owner = ActionOwner(
        display_name="DBA",
    )

    assert first_owner == second_owner
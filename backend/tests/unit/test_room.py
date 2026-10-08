from uuid import uuid4

import pytest

from onair.core.errors import ConflictError
from onair.modules.rooms.domain.room import NotHostError, Room, RoomStatus


def test_first_member_becomes_host_and_host_passes_on_leave() -> None:
    room = Room("r", max_players=4)
    a, b = uuid4(), uuid4()
    room.join(a, "a")
    room.join(b, "b")
    assert room.host_id == a

    room.leave(a)
    assert room.host_id == b


def test_room_rejects_when_full() -> None:
    room = Room("r", max_players=1)
    room.join(uuid4(), "a")
    with pytest.raises(ConflictError):
        room.join(uuid4(), "b")


def test_only_host_starts_and_everyone_else_must_be_ready() -> None:
    room = Room("r", max_players=4)
    host, guest = uuid4(), uuid4()
    room.join(host, "h")
    room.join(guest, "g")

    with pytest.raises(NotHostError):
        room.start(guest)
    with pytest.raises(ConflictError):
        room.start(host)

    room.set_ready(guest, True)
    room.start(host)
    assert room.status is RoomStatus.PLAYING

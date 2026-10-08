from onair.modules.match.domain.notifications import (
    ItemPicked,
    MatchFinished,
    Notification,
    PhaseStarted,
    ScoreEntry,
    StaticsChanged,
)
from onair.modules.match.domain.session import EntityView, GameSession
from onair.protocol.base import Message
from onair.protocol.server import (
    EntityState,
    ItemOffer,
    ItemPickedMessage,
    LevelItemsMessage,
    LevelLayout,
    MatchEndedMessage,
    MatchPlayer,
    MatchStartedMessage,
    PhaseChangedMessage,
    ScoreLine,
    SnapshotMessage,
)


class MatchPresenter:
    """Maps domain views/notifications to wire messages."""

    def __init__(self, simulation_hz: int) -> None:
        self._simulation_hz = simulation_hz

    def match_started(self, session: GameSession) -> MatchStartedMessage:
        ctx = session.context
        level = ctx.level.definition
        return MatchStartedMessage(
            level=LevelLayout(
                key=level.key,
                width=level.width,
                height=level.height,
                tile_size=level.tile_size,
                rows=list(level.rows),
            ),
            players=[
                MatchPlayer(player_id=p.player_id, username=p.username, color=p.color)
                for p in ctx.participants.values()
            ],
            target_score=ctx.rules.scoring.target,
            simulation_hz=self._simulation_hz,
        )

    def snapshot(self, session: GameSession) -> SnapshotMessage:
        view = session.snapshot()
        return SnapshotMessage(
            tick=view.tick,
            phase_time_left=round(view.phase_time_left, 2),
            acks={str(pid): seq for pid, seq in view.acks.items()},
            entities=[self._entity(e) for e in view.entities],
        )

    def notification(self, session: GameSession, notification: Notification) -> Message:
        match notification:
            case PhaseStarted():
                return PhaseChangedMessage(
                    phase=notification.phase,
                    round=notification.round,
                    duration=notification.duration,
                    offers=[
                        ItemOffer(offer_id=o.offer_id, item=o.item, taken_by=o.taken_by)
                        for o in notification.offers
                    ]
                    if notification.offers is not None
                    else None,
                    scores=self._scores(notification.scores)
                    if notification.scores is not None
                    else None,
                )
            case ItemPicked():
                return ItemPickedMessage(
                    player_id=notification.player_id,
                    offer_id=notification.offer_id,
                    item=notification.item,
                )
            case StaticsChanged():
                return LevelItemsMessage(items=[self._entity(e) for e in session.statics()])
            case MatchFinished():
                return MatchEndedMessage(
                    winner_id=notification.winner_id, scores=self._scores(notification.scores)
                )

    @staticmethod
    def _scores(entries: tuple[ScoreEntry, ...]) -> list[ScoreLine]:
        return [
            ScoreLine(
                player_id=e.player_id, total=e.total, gained=e.gained, reasons=list(e.reasons)
            )
            for e in entries
        ]

    @staticmethod
    def _entity(view: EntityView) -> EntityState:
        return EntityState(
            id=view.id,
            kind=view.kind,
            x=view.x,
            y=view.y,
            w=view.w,
            h=view.h,
            vx=view.vx,
            vy=view.vy,
            player_id=view.player_id,
            state=view.state,  # type: ignore[arg-type]
        )

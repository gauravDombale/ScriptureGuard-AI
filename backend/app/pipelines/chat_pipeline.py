from dataclasses import dataclass, field
from collections.abc import AsyncIterator
from typing import Any, TypedDict
from uuid import UUID

from app.models.schemas import ChatResponse, VerseCitation
from app.services.bible_retriever import BibleRetriever, VerseChunk
from app.services.denomination_service import denomination_note
from app.services.historical_fact_checker import HistoricalFactChecker
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.safety_service import SafetyService, graceful_theological_response
from app.services.verse_validator import VerseValidator


@dataclass
class PipelineState:
    session_id: UUID
    message: str
    denomination: str
    safety_blocked: bool = False
    block_reason: str | None = None
    block_category: str | None = None
    sensitive_topic: str | None = None
    retrieved_verses: list[VerseChunk] = field(default_factory=list)
    memory_context: list[dict] = field(default_factory=list)
    raw_response: str = ""
    citations: list[VerseCitation] = field(default_factory=list)
    retrieval_score: float | None = None


class PipelineStateDict(TypedDict, total=False):
    session_id: UUID
    message: str
    denomination: str
    safety_blocked: bool
    block_reason: str | None
    block_category: str | None
    sensitive_topic: str | None
    retrieved_verses: list[VerseChunk]
    memory_context: list[dict]
    raw_response: str
    citations: list[VerseCitation]
    retrieval_score: float | None


class ChatPipeline:
    def __init__(self, memory: MemoryService | None = None) -> None:
        self.safety = SafetyService()
        self.retriever = BibleRetriever()
        self.llm = LLMService()
        self.validator = VerseValidator()
        self.fact_checker = HistoricalFactChecker()
        self.memory = memory or MemoryService()
        self.graph = self._build_graph()

    async def run(self, session_id: UUID, message: str, denomination: str) -> ChatResponse:
        state = PipelineState(session_id=session_id, message=message, denomination=denomination)
        if self.graph is not None:
            state = state_from_dict(await self.graph.ainvoke(state_to_dict(state)))
        else:
            state = await self._run_direct(state)

        if state.safety_blocked:
            await self.log_memory(state, assistant_response=state.block_reason or "")
            return ChatResponse(
                session_id=session_id,
                response=state.block_reason or "I cannot help with that request.",
                citations=[],
                safety_blocked=True,
                block_reason=state.block_reason,
                denomination_notes=denomination_note(denomination),
            )

        if state.sensitive_topic:
            state.raw_response = graceful_theological_response(state.sensitive_topic, denomination)
            await self.log_memory(state, assistant_response=state.raw_response)
            return ChatResponse(
                session_id=session_id,
                response=state.raw_response,
                citations=[],
                denomination_notes=denomination_note(denomination),
            )

        if state.block_category == "missing_reference":
            await self.log_memory(state, assistant_response=state.raw_response)
            return ChatResponse(
                session_id=session_id,
                response=state.raw_response,
                citations=[],
                denomination_notes=denomination_note(denomination),
            )

        await self.log_memory(state, assistant_response=state.raw_response)

        return ChatResponse(
            session_id=session_id,
            response=state.raw_response,
            citations=state.citations,
            safety_blocked=False,
            denomination_notes=denomination_note(denomination),
            retrieval_score=state.retrieval_score,
        )

    async def stream(self, session_id: UUID, message: str, denomination: str) -> AsyncIterator[dict]:
        state = PipelineState(session_id=session_id, message=message, denomination=denomination)
        yield {"type": "status", "message": "Checking request safety..."}
        state = await self.safety_guard(state)
        if state.safety_blocked:
            await self.log_memory(state, assistant_response=state.block_reason or "")
            yield {
                "type": "final",
                "session_id": str(session_id),
                "response": state.block_reason or "I cannot help with that request.",
                "citations": [],
                "safety_blocked": True,
                "block_reason": state.block_reason,
                "denomination_notes": denomination_note(denomination),
                "retrieval_score": None,
            }
            return

        state = await self.intent_router(state)
        if state.sensitive_topic:
            response = graceful_theological_response(state.sensitive_topic, denomination)
            state.raw_response = response
            await self.log_memory(state, assistant_response=response)
            yield {
                "type": "final",
                "session_id": str(session_id),
                "response": response,
                "citations": [],
                "safety_blocked": False,
                "block_reason": None,
                "denomination_notes": denomination_note(denomination),
                "retrieval_score": None,
            }
            return

        state = await self.missing_reference_node(state)
        if state.block_category == "missing_reference":
            await self.log_memory(state, assistant_response=state.raw_response)
            yield {
                "type": "final",
                "session_id": str(session_id),
                "response": state.raw_response,
                "citations": [],
                "safety_blocked": False,
                "block_reason": None,
                "denomination_notes": denomination_note(denomination),
                "retrieval_score": None,
            }
            return

        yield {"type": "status", "message": "Retrieving verified scripture context..."}
        state = await self.bible_retriever(state)
        yield {"type": "status", "message": "Generating grounded response..."}

        chunks: list[str] = []
        async for chunk in self.llm.stream_response(
            state.message, state.denomination, state.retrieved_verses, state.memory_context
        ):
            chunks.append(chunk)
            yield {"type": "delta", "content": chunk}

        state.raw_response = "".join(chunks)
        yield {"type": "status", "message": "Validating citations..."}
        state = await self.verse_validator_node(state)
        state = await self.historical_fact_checker_node(state)
        await self.log_memory(state, assistant_response=state.raw_response)
        yield {
            "type": "final",
            "session_id": str(session_id),
            "response": state.raw_response,
            "citations": [citation.model_dump() for citation in state.citations],
            "safety_blocked": False,
            "block_reason": None,
            "denomination_notes": denomination_note(denomination),
            "retrieval_score": state.retrieval_score,
        }

    async def _run_direct(self, state: PipelineState) -> PipelineState:
        state = await self.safety_guard(state)
        if state.safety_blocked:
            return state
        state = await self.intent_router(state)
        if state.sensitive_topic:
            return state
        state = await self.missing_reference_node(state)
        if state.block_category == "missing_reference":
            return state
        state = await self.bible_retriever(state)
        state = await self.llm_node(state)
        state = await self.verse_validator_node(state)
        return await self.historical_fact_checker_node(state)

    def _build_graph(self) -> Any | None:
        try:
            from langgraph.graph import END, START, StateGraph

            graph = StateGraph(PipelineStateDict)
            graph.add_node("safety_guard", self._graph_node(self.safety_guard))
            graph.add_node("intent_router", self._graph_node(self.intent_router))
            graph.add_node("missing_reference", self._graph_node(self.missing_reference_node))
            graph.add_node("bible_retriever", self._graph_node(self.bible_retriever))
            graph.add_node("llm_node", self._graph_node(self.llm_node))
            graph.add_node("verse_validator", self._graph_node(self.verse_validator_node))
            graph.add_node(
                "historical_fact_checker", self._graph_node(self.historical_fact_checker_node)
            )

            graph.add_edge(START, "safety_guard")
            graph.add_conditional_edges(
                "safety_guard",
                lambda state: "blocked" if state.get("safety_blocked") else "continue",
                {"blocked": END, "continue": "intent_router"},
            )
            graph.add_conditional_edges(
                "intent_router",
                lambda state: "sensitive" if state.get("sensitive_topic") else "continue",
                {"sensitive": END, "continue": "missing_reference"},
            )
            graph.add_conditional_edges(
                "missing_reference",
                lambda state: "missing"
                if state.get("block_category") == "missing_reference"
                else "continue",
                {"missing": END, "continue": "bible_retriever"},
            )
            graph.add_edge("bible_retriever", "llm_node")
            graph.add_edge("llm_node", "verse_validator")
            graph.add_edge("verse_validator", "historical_fact_checker")
            graph.add_edge("historical_fact_checker", END)
            return graph.compile()
        except Exception:
            return None

    def _graph_node(self, func):
        async def wrapped(state: PipelineStateDict) -> PipelineStateDict:
            result = await func(state_from_dict(state))
            return state_to_dict(result)

        return wrapped

    async def safety_guard(self, state: PipelineState) -> PipelineState:
        result = await self.safety.check(state.message)
        if result.blocked:
            state.safety_blocked = True
            state.block_reason = result.reason
            state.block_category = result.category
        return state

    async def intent_router(self, state: PipelineState) -> PipelineState:
        state.sensitive_topic = self.safety.sensitive_topic(state.message)
        return state

    async def missing_reference_node(self, state: PipelineState) -> PipelineState:
        missing = self.validator.explain_missing_reference(state.message)
        if missing:
            state.block_category = "missing_reference"
            state.raw_response = missing
        return state

    async def bible_retriever(self, state: PipelineState) -> PipelineState:
        state.memory_context = await self.memory.get_context(str(state.session_id))
        state.retrieved_verses = await self.retriever.retrieve_verses(
            state.message, state.denomination
        )
        if state.retrieved_verses:
            state.retrieval_score = round(
                sum(verse.score for verse in state.retrieved_verses) / len(state.retrieved_verses),
                3,
            )
        return state

    async def llm_node(self, state: PipelineState) -> PipelineState:
        state.raw_response = await self.llm.generate_response(
            state.message, state.denomination, state.retrieved_verses, state.memory_context
        )
        return state

    async def verse_validator_node(self, state: PipelineState) -> PipelineState:
        validation = self.validator.validate_citations(state.raw_response)
        state.raw_response = validation.cleaned_response
        state.citations = validation.valid_citations
        if not state.citations and state.retrieved_verses:
            seen_references: set[str] = set()
            fallback_citations: list[VerseCitation] = []
            for verse in state.retrieved_verses:
                if verse.reference in seen_references:
                    continue
                seen_references.add(verse.reference)
                fallback_citations.append(
                    VerseCitation(reference=verse.reference, text=verse.text, verified=True)
                )
            warning = (
                "\n\nNote: I could not verify one or more references, so I removed or flagged them. "
                "Please consult your Bible directly."
            )
            clean_response = state.raw_response.replace(warning, "").rstrip()
            state.raw_response = (
                clean_response
                + "\n\nVerified KJV references:\n"
                + "\n".join(
                    f'[{citation.reference}] "{citation.text}"'
                    for citation in fallback_citations
                )
            )
            state.citations = fallback_citations
        return state

    async def historical_fact_checker_node(self, state: PipelineState) -> PipelineState:
        checked = await self.fact_checker.check(state.raw_response)
        state.raw_response = checked.text
        return state

    async def log_memory(self, state: PipelineState, assistant_response: str) -> None:
        await self.memory.append_turn(str(state.session_id), "user", state.message)
        await self.memory.append_turn(
            str(state.session_id),
            "assistant",
            assistant_response,
            {"citations": [citation.model_dump() for citation in state.citations]},
        )


def state_to_dict(state: PipelineState) -> PipelineStateDict:
    return state.__dict__.copy()


def state_from_dict(state: PipelineStateDict) -> PipelineState:
    pipeline_state = PipelineState(
        session_id=state["session_id"],
        message=state["message"],
        denomination=state["denomination"],
    )
    for key, value in state.items():
        setattr(pipeline_state, key, value)
    return pipeline_state

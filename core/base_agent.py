from __future__ import annotations

from abc import ABC, abstractmethod

from shared.schemas import AgentAnalyzeRequest, AgentAnalyzeResponse, AgentMetadata


class BaseAgent(ABC):
    name: str
    version: str = "1.0.0"
    description: str = ""
    supported_inputs: list[str] = []
    supported_outputs: list[str] = []
    required_dependencies: list[str] = []

    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name=self.name,
            version=self.version,
            description=self.description,
            supported_inputs=self.supported_inputs,
            supported_outputs=self.supported_outputs,
            required_dependencies=self.required_dependencies,
        )

    @abstractmethod
    def analyze(self, request: AgentAnalyzeRequest) -> AgentAnalyzeResponse:
        raise NotImplementedError


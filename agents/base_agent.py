"""基础 Agent 类"""
from typing import List, Callable, Optional, TypedDict
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


class AgentState(TypedDict):
    """Agent 状态"""
    messages: List[BaseMessage]
    next_step: str


@dataclass
class ToolInfo:
    """工具信息"""
    name: str
    description: str
    func: Callable


class BaseAgent:
    """基础 Agent 类"""

    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
    ):
        """
        初始化 Agent

        Args:
            llm: LLM 实例
            system_prompt: 系统提示词
            tools: 工具列表
        """
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.tool_map = {tool.name: tool for tool in self.tools}

        # 构建工作流
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        # 定义状态图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("agent", self._agent_node)
        if self.tools:
            workflow.add_node("tools", ToolNode(self.tools))

        # 添加边
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools" if self.tools else END,
                "end": END,
            },
        )
        if self.tools:
            workflow.add_edge("tools", "agent")

        return workflow.compile()

    def _agent_node(self, state: AgentState) -> AgentState:
        """Agent 节点"""
        messages = state["messages"]

        # 添加系统提示词
        if self.system_prompt and not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=self.system_prompt)] + messages

        # 调用 LLM
        response = self.llm.invoke(messages)

        return {
            "messages": messages + [response],
            "next_step": "continue" if self._has_tool_calls(response) else "end",
        }

    def _should_continue(self, state: AgentState) -> str:
        """判断是否继续"""
        return state.get("next_step", "end")

    def _has_tool_calls(self, message: BaseMessage) -> bool:
        """检查消息是否包含工具调用"""
        return hasattr(message, 'tool_calls') and message.tool_calls

    def run(self, input_text: str, stream: bool = False) -> str:
        """
        运行 Agent

        Args:
            input_text: 输入文本
            stream: 是否流式输出

        Returns:
            Agent 响应
        """
        initial_state = {
            "messages": [HumanMessage(content=input_text)],
            "next_step": "continue",
        }

        if stream:
            return self._run_stream(initial_state)

        # 执行工作流
        final_state = self.workflow.invoke(initial_state)

        # 返回最后一条 AI 消息
        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content

        return ""

    def _run_stream(self, initial_state: AgentState):
        """流式运行"""
        for state in self.workflow.stream(initial_state):
            messages = state.get("messages", [])
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, AIMessage):
                    yield last_msg.content

    def register_tool(self, tool: BaseTool) -> None:
        """
        注册工具

        Args:
            tool: 工具实例
        """
        self.tools.append(tool)
        self.tool_map[tool.name] = tool
        # 重新构建工作流
        self.workflow = self._build_workflow()

    def register_skills(self, skills_module) -> None:
        """
        注册技能模块

        Args:
            skills_module: 技能模块
        """
        if hasattr(skills_module, 'get_tools'):
            tools = skills_module.get_tools()
            for tool in tools:
                self.register_tool(tool)


class SimpleAgent(BaseAgent):
    """简单 Agent（无工具）"""

    def __init__(self, llm: BaseChatModel, system_prompt: Optional[str] = None):
        super().__init__(llm, system_prompt, tools=[])

    def run(self, input_text: str) -> str:
        """运行简单对话"""
        messages = []
        if self.system_prompt:
            messages.append(SystemMessage(content=self.system_prompt))
        messages.append(HumanMessage(content=input_text))

        response = self.llm.invoke(messages)
        return response.content if hasattr(response, 'content') else str(response)

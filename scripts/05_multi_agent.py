"""
示例 5: Multi-Agent 多智能体协作系统
演示多个专业智能体如何协作完成复杂任务
Key Words: Multi-Agent, Collaboration, Workflow, State Graph, DAG
"""
import sys
from pathlib import Path
from typing import List, TypedDict, Annotated, Sequence
from dataclasses import dataclass, field
import operator

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from core.llm_init import get_llm
from core.config import check_api_key


# =============================================================================
# 多智能体系统状态定义
# =============================================================================

class MultiAgentState(TypedDict):
    """多智能体系统状态"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_agent: str  # 当前正在执行的智能体
    task_type: str      # 任务类型
    research_result: str  # 研究结果
    analysis_result: str  # 分析结果
    final_answer: str   # 最终答案
    next_step: str      # 下一步
    review_passed: bool  # 审核是否通过
    review_feedback: str  # 审核反馈
    iteration_count: int  # 迭代次数（防止无限循环）


# =============================================================================
# 专业智能体定义
# =============================================================================

@dataclass
class SpecialistAgent:
    """专业智能体"""
    name: str
    role: str
    system_prompt: str
    llm: any = field(default=None)
    
    def invoke(self, messages: List[BaseMessage]) -> str:
        """执行智能体"""
        full_messages = [SystemMessage(content=self.system_prompt)] + list(messages)
        response = self.llm.invoke(full_messages)
        return response.content if hasattr(response, 'content') else str(response)


class ResearchAgent(SpecialistAgent):
    """研究智能体 - 负责信息收集和调研"""
    
    def __init__(self, llm):
        super().__init__(
            name="researcher",
            role="研究专家",
            system_prompt="""你是一位专业的研究专家。你的职责是：
1. 深入理解用户的问题和需求
2. 收集相关信息和背景知识
3. 提供全面、准确的信息调研结果
4. 列出关键点和需要考虑的因素

输出格式：
【研究摘要】简要概括研究主题
【关键信息】列出3-5个关键信息点
【相关因素】列出需要考虑的相关因素
【建议方向】给出后续处理建议""",
            llm=llm
        )


class AnalysisAgent(SpecialistAgent):
    """分析智能体 - 负责数据分析和逻辑推理"""
    
    def __init__(self, llm):
        super().__init__(
            name="analyst",
            role="分析专家",
            system_prompt="""你是一位专业的分析专家。你的职责是：
1. 分析研究专家提供的信息
2. 进行逻辑推理和深度分析
3. 识别潜在的问题和机会
4. 提供结构化的分析结论

输出格式：
【分析框架】使用的分析方法和框架
【深度分析】详细的分析过程和推理
【关键洞察】2-3个重要发现
【风险评估】潜在的风险和注意事项""",
            llm=llm
        )


class SolutionAgent(SpecialistAgent):
    """方案智能体 - 负责生成解决方案"""
    
    def __init__(self, llm):
        super().__init__(
            name="strategist",
            role="方案专家",
            system_prompt="""你是一位专业的方案专家。你的职责是：
1. 基于研究和分析结果制定解决方案
2. 提供具体、可执行的建议
3. 考虑实际可行性和实施步骤
4. 给出清晰的行动指南

输出格式：
【解决方案】核心解决方案概述
【实施步骤】分步骤的实施计划
【预期效果】预期达成的效果
【注意事项】实施过程中的注意要点""",
            llm=llm
        )


class ReviewAgent(SpecialistAgent):
    """审核智能体 - 负责质量检查和优化"""
    
    def __init__(self, llm):
        super().__init__(
            name="reviewer",
            role="审核专家",
            system_prompt="""你是一位专业的审核专家。你的职责是：
1. 审核整个解决方案的完整性和准确性
2. 检查是否有遗漏或错误
3. 提出改进建议
4. 给出最终的质量评估

重要：你必须在输出开头明确给出审核结论：
【审核结论】通过 / 不通过

如果审核不通过，请详细说明需要修改的地方。

输出格式：
【审核结论】通过 或 不通过
【质量评估】整体质量评分(A/B/C/D)和理由
【完整性检查】是否完整覆盖了所有需求
【改进建议】具体的优化建议（如不通过，必须详细说明）
【最终输出】整合后的最终回答（如通过）或修改要求（如不通过）""",
            llm=llm
        )


# =============================================================================
# 多智能体系统
# =============================================================================

class MultiAgentSystem:
    """多智能体协作系统"""
    
    def __init__(self, llm):
        self.llm = llm
        
        # 初始化各专业智能体
        self.agents = {
            "researcher": ResearchAgent(llm),
            "analyst": AnalysisAgent(llm),
            "strategist": SolutionAgent(llm),
            "reviewer": ReviewAgent(llm),
        }
        
        # 构建工作流
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """构建多智能体协作工作流（支持条件分支）"""
        
        # 定义状态图
        workflow = StateGraph(MultiAgentState)
        
        # 添加节点
        workflow.add_node("researcher", self._research_node)
        workflow.add_node("analyst", self._analysis_node)
        workflow.add_node("strategist", self._solution_node)
        workflow.add_node("reviewer", self._review_node)
        
        # 设置入口
        workflow.set_entry_point("researcher")
        
        # 添加边 - 顺序执行流程
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "strategist")
        
        # 添加条件边：审核后根据结果决定流向
        workflow.add_edge("strategist", "reviewer")
        workflow.add_conditional_edges(
            "reviewer",
            self._check_review_result,
            {
                "approved": END,        # 审核通过，结束
                "rejected": "strategist",  # 审核不通过，返回修改
                "max_iterations": END,  # 达到最大迭代次数，强制结束
            }
        )
        
        return workflow.compile()
    
    def _check_review_result(self, state: MultiAgentState) -> str:
        """检查审核结果，决定下一步流向"""
        # 检查是否达到最大迭代次数（防止无限循环）
        if state.get("iteration_count", 0) >= 3:
            print("\n⚠️  已达到最大迭代次数，强制结束")
            return "max_iterations"
        
        # 检查审核是否通过
        if state.get("review_passed", False):
            print("\n✅ 审核通过，流程结束")
            return "approved"
        else:
            print(f"\n🔄 审核不通过，返回修改（第 {state.get('iteration_count', 0)} 轮）")
            return "rejected"
    
    def _research_node(self, state: MultiAgentState) -> MultiAgentState:
        """研究节点"""
        print("\n🔍 [研究智能体] 正在收集信息...")
        
        agent = self.agents["researcher"]
        messages = list(state["messages"])
        
        result = agent.invoke(messages)
        
        print("✅ [研究智能体] 完成信息收集")
        
        return {
            **state,
            "current_agent": "researcher",
            "research_result": result,
            "messages": messages + [AIMessage(content=f"[研究阶段]\n{result}")]
        }
    
    def _analysis_node(self, state: MultiAgentState) -> MultiAgentState:
        """分析节点"""
        print("\n📊 [分析智能体] 正在进行深度分析...")
        
        agent = self.agents["analyst"]
        
        # 构建分析输入，包含研究结果
        analysis_input = [
            HumanMessage(content=f"""请基于以下研究结果进行分析：

{state['research_result']}

原始问题：{state['messages'][0].content}""")
        ]
        
        result = agent.invoke(analysis_input)
        
        print("✅ [分析智能体] 完成分析")
        
        return {
            **state,
            "current_agent": "analyst",
            "analysis_result": result,
            "messages": list(state["messages"]) + [AIMessage(content=f"[分析阶段]\n{result}")]
        }
    
    def _solution_node(self, state: MultiAgentState) -> MultiAgentState:
        """方案节点"""
        iteration = state.get("iteration_count", 0)
        if iteration > 0:
            print(f"\n💡 [方案智能体] 正在根据反馈修改方案（第 {iteration} 轮）...")
        else:
            print("\n💡 [方案智能体] 正在制定解决方案...")
        
        agent = self.agents["strategist"]
        
        # 构建方案输入，包含研究和分析结果
        if iteration > 0 and state.get("review_feedback"):
            # 如果有审核反馈，包含反馈信息
            solution_input = [
                HumanMessage(content=f"""请基于以下研究和分析结果制定解决方案：

=== 研究结果 ===
{state['research_result']}

=== 分析结果 ===
{state['analysis_result']}

原始问题：{state['messages'][0].content}

=== 审核反馈（请重点改进）===
{state['review_feedback']}

注意：这是第 {iteration} 轮修改，请根据审核反馈重点改进上述问题。""")
            ]
        else:
            solution_input = [
                HumanMessage(content=f"""请基于以下研究和分析结果制定解决方案：

=== 研究结果 ===
{state['research_result']}

=== 分析结果 ===
{state['analysis_result']}

原始问题：{state['messages'][0].content}""")
            ]
        
        result = agent.invoke(solution_input)
        
        if iteration > 0:
            print(f"✅ [方案智能体] 完成方案修改（第 {iteration} 轮）")
        else:
            print("✅ [方案智能体] 完成方案制定")
        
        return {
            **state,
            "current_agent": "strategist",
            "final_answer": result,
            "messages": list(state["messages"]) + [AIMessage(content=f"[方案阶段{'-修改' + str(iteration) if iteration > 0 else ''}]\n{result}")]
        }
    
    def _review_node(self, state: MultiAgentState) -> MultiAgentState:
        """审核节点"""
        iteration = state.get("iteration_count", 0) + 1
        print(f"\n✅ [审核智能体] 正在进行质量审核（第 {iteration} 轮）...")
        
        agent = self.agents["reviewer"]
        
        # 构建审核输入
        review_input = [
            HumanMessage(content=f"""请审核以下完整方案：

=== 原始问题 ===
{state['messages'][0].content}

=== 研究结果 ===
{state['research_result']}

=== 分析结果 ===
{state['analysis_result']}

=== 解决方案 ===
{state['final_answer']}

请给出最终审核结果和优化后的完整回答。""")
        ]
        
        result = agent.invoke(review_input)
        
        # 解析审核结果，判断是否通过
        review_passed = self._parse_review_result(result)
        
        if review_passed:
            print(f"✅ [审核智能体] 审核通过（第 {iteration} 轮）")
        else:
            print(f"❌ [审核智能体] 审核不通过（第 {iteration} 轮），需要修改")
        
        return {
            **state,
            "current_agent": "reviewer",
            "final_answer": result if review_passed else state["final_answer"],
            "review_passed": review_passed,
            "review_feedback": result if not review_passed else "",
            "iteration_count": iteration,
            "messages": list(state["messages"]) + [AIMessage(content=f"[审核阶段-{iteration}]\n{result}")]
        }
    
    def _parse_review_result(self, review_result: str) -> bool:
        """解析审核结果，判断是否通过"""
        # 检查审核结论中是否包含"通过"
        review_lower = review_result.lower()
        
        # 查找【审核结论】部分
        if "【审核结论】" in review_result:
            # 提取审核结论行的内容
            for line in review_result.split("\n"):
                if "【审核结论】" in line:
                    # 如果包含"不通过"或"未通过"，则返回False
                    if "不通过" in line or "未通过" in line or "失败" in line:
                        return False
                    # 如果包含"通过"，则返回True
                    if "通过" in line or "合格" in line or "approved" in line.lower():
                        return True
        
        # 默认策略：检查是否有明显的负面关键词
        negative_keywords = ["不通过", "未通过", "不合格", "需要修改", "重大缺陷", "严重问题"]
        for keyword in negative_keywords:
            if keyword in review_lower:
                return False
        
        # 如果没有明确的负面词，默认为通过
        return True
    
    def run(self, query: str) -> dict:
        """运行多智能体系统"""
        
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "current_agent": "",
            "task_type": "",
            "research_result": "",
            "analysis_result": "",
            "final_answer": "",
            "next_step": "researcher",
            "review_passed": False,
            "review_feedback": "",
            "iteration_count": 0
        }
        
        # 执行工作流
        final_state = self.workflow.invoke(initial_state)
        
        return final_state


# =============================================================================
# 演示场景
# =============================================================================

def demo_multi_agent_collaboration():
    """演示多智能体协作"""
    print("\n" + "=" * 70)
    print("🤖 Multi-Agent 多智能体协作演示（带条件分支）")
    print("=" * 70)
    print("""
本演示展示了一个多智能体协作系统，包含4个专业智能体：

                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  研究智能体  │───▶│  分析智能体  │───▶│  方案智能体  │───▶│  审核智能体  │
│  Researcher │    │   Analyst   │    │  Strategist │    │   Reviewer  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      🔍                 📊                 💡                 ✅
   信息收集           深度分析            制定方案            质量审核
                                                              │
                                                              ▼
                                                    ┌─────────────────┐
                                                    │  条件分支判断    │
                                                    └────────┬────────┘
                                                             │
                                    ┌────────────────────────┼────────────────────────┐
                                    │                        │                        │
                                    ▼                        ▼                        ▼
                              ┌─────────┐            ┌─────────────┐          ┌─────────────┐
                              │  不通过  │───────────▶│  返回修改    │          │   通过      │
                              │ rejected │            │ strategist  │          │  approved   │
                              └─────────┘            └─────────────┘          └──────┬──────┘
                                                                                     │
                                                                                     ▼
                                                                              ┌─────────────┐
                                                                              │    结束     │
                                                                              │     END     │
                                                                              └─────────────┘

工作流程：
1. 研究智能体收集相关信息
2. 分析智能体进行深度分析
3. 方案智能体制定解决方案
4. 审核智能体进行质量检查
5. 【条件分支】根据审核结果：
   - 通过 → 流程结束
   - 不通过 → 返回方案智能体修改（最多3轮）
   - 达到最大迭代次数 → 强制结束
""")
    
    # 初始化 LLM
    provider = "openai" if check_api_key("openai") else "ollama"
    print(f"\n📡 使用模型提供商: {provider}")
    
    try:
        llm = get_llm(provider=provider, temperature=0.7)
    except Exception as e:
        print(f"❌ 初始化 LLM 失败: {e}")
        return
    
    # 创建多智能体系统
    system = MultiAgentSystem(llm)
    
    # 测试问题
    test_queries = [
        "我想学习Python编程，请给我制定一个3个月的学习计划",
        "如何准备一场技术面试？",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"📝 任务 {i}: {query}")
        print("=" * 70)
        
        # 运行多智能体系统
        result = system.run(query)
        
        # 输出最终结果
        print("\n" + "=" * 70)
        print("📋 最终结果")
        print("=" * 70)
        print(result["final_answer"])
        print("\n" + "=" * 70)
        input("\n按 Enter 继续下一个示例...")


def demo_agent_debate():
    """演示智能体辩论模式"""
    print("\n" + "=" * 70)
    print("🗣️  智能体辩论模式演示")
    print("=" * 70)
    print("""
本演示展示多个智能体从不同角度讨论一个话题：
- 正方观点智能体
- 反方观点智能体
- 中立总结智能体
""")
    
    provider = "openai" if check_api_key("openai") else "ollama"
    
    try:
        llm = get_llm(provider=provider, temperature=0.8)
    except Exception as e:
        print(f"❌ 初始化 LLM 失败: {e}")
        return
    
    # 定义辩论话题
    topic = "人工智能是否会取代程序员？"
    
    print(f"\n📢 辩论话题: {topic}")
    print("\n" + "-" * 70)
    
    # 正方观点
    print("\n👍 [正方智能体] 观点：")
    pro_prompt = f"""你是正方辩手。请就以下话题阐述支持的观点，给出3-5个有力的论据：

话题：{topic}

要求：
1. 观点明确，论据充分
2. 每个论据都要有具体说明
3. 语言有说服力"""
    
    pro_response = llm.invoke([HumanMessage(content=pro_prompt)])
    print(pro_response.content if hasattr(pro_response, 'content') else str(pro_response))
    
    print("\n" + "-" * 70)
    
    # 反方观点
    print("\n👎 [反方智能体] 观点：")
    con_prompt = f"""你是反方辩手。请就以下话题阐述反对的观点，给出3-5个有力的论据：

话题：{topic}

要求：
1. 观点明确，论据充分
2. 每个论据都要有具体说明
3. 语言有说服力"""
    
    con_response = llm.invoke([HumanMessage(content=con_prompt)])
    print(con_response.content if hasattr(con_response, 'content') else str(con_response))
    
    print("\n" + "-" * 70)
    
    # 中立总结
    print("\n⚖️  [总结智能体] 综合观点：")
    summary_prompt = f"""你是中立总结者。请基于以下正反方观点，给出客观、全面的总结：

话题：{topic}

正方观点：
{pro_response.content if hasattr(pro_response, 'content') else str(pro_response)}

反方观点：
{con_response.content if hasattr(con_response, 'content') else str(con_response)}

要求：
1. 客观公正，不偏向任何一方
2. 总结双方的核心论点
3. 给出平衡的观点和结论"""
    
    summary_response = llm.invoke([HumanMessage(content=summary_prompt)])
    print(summary_response.content if hasattr(summary_response, 'content') else str(summary_response))


def demo_hierarchical_agents():
    """演示层级智能体系统"""
    print("\n" + "=" * 70)
    print("🏢 层级智能体系统演示")
    print("=" * 70)
    print("""
本演示展示一个层级化的智能体系统：
- 主管智能体：分配任务
- 执行智能体：具体执行
- 汇报智能体：汇总结果

工作流程：
主管分析任务 → 分解子任务 → 分配给执行智能体 → 收集结果 → 汇总汇报
""")
    
    provider = "openai" if check_api_key("openai") else "ollama"
    
    try:
        llm = get_llm(provider=provider, temperature=0.7)
    except Exception as e:
        print(f"❌ 初始化 LLM 失败: {e}")
        return
    
    # 复杂任务
    complex_task = "帮我规划一个为期一周的北京旅游行程"
    
    print(f"\n📋 复杂任务: {complex_task}")
    print("\n" + "=" * 70)
    
    # 步骤1: 主管智能体分解任务
    print("\n👔 [主管智能体] 任务分解：")
    manager_prompt = f"""你是任务主管。请将以下复杂任务分解为3-4个子任务：

任务：{complex_task}

要求：
1. 每个子任务要具体明确
2. 说明子任务之间的依赖关系
3. 为每个子任务分配执行智能体（景点研究员、美食专家、交通规划师等）

输出格式：
子任务1：[任务描述] - 分配给 [智能体名称]
子任务2：[任务描述] - 分配给 [智能体名称]
..."""
    
    manager_response = llm.invoke([HumanMessage(content=manager_prompt)])
    decomposition = manager_response.content if hasattr(manager_response, 'content') else str(manager_response)
    print(decomposition)
    
    # 步骤2: 模拟各执行智能体工作
    print("\n" + "=" * 70)
    print("\n🔧 [执行智能体] 并行执行任务：")
    
    sub_tasks = [
        ("景点研究员", "列出北京必去的5-7个著名景点，包括简介和游玩时间"),
        ("美食专家", "推荐北京的特色美食和餐厅，包括早餐、午餐、晚餐"),
        ("交通规划师", "规划北京市内的交通方式，包括地铁、公交、打车建议"),
    ]
    
    results = []
    for agent_name, sub_task in sub_tasks:
        print(f"\n  📌 {agent_name} 正在工作...")
        
        worker_prompt = f"""你是{agent_name}。请完成以下任务：

任务：{sub_task}

背景：这是为"{complex_task}"的一部分

要求：
1. 内容具体实用
2. 格式清晰易读"""
        
        worker_response = llm.invoke([HumanMessage(content=worker_prompt)])
        result = worker_response.content if hasattr(worker_response, 'content') else str(worker_response)
        results.append((agent_name, result))
        print(f"  ✅ {agent_name} 完成")
    
    # 步骤3: 汇报智能体汇总
    print("\n" + "=" * 70)
    print("\n📊 [汇报智能体] 汇总整合：")
    
    all_results = "\n\n".join([f"=== {name} ===\n{result}" for name, result in results])
    
    reporter_prompt = f"""你是汇报智能体。请将以下各执行智能体的结果整合为一份完整的旅游攻略：

原始任务：{complex_task}

各智能体执行结果：
{all_results}

要求：
1. 按天组织行程（第1天、第2天...）
2. 每天包含：景点、美食、交通
3. 给出实用的建议和注意事项
4. 格式清晰，便于阅读"""
    
    reporter_response = llm.invoke([HumanMessage(content=reporter_prompt)])
    final_report = reporter_response.content if hasattr(reporter_response, 'content') else str(reporter_response)
    print(final_report)


def print_concepts():
    """打印多智能体核心概念"""
    print("\n" + "=" * 70)
    print("📚 Multi-Agent 核心概念")
    print("=" * 70)
    
    concepts = """
【什么是 Multi-Agent 系统？】

Multi-Agent 系统是由多个智能体（Agent）组成的协作系统，每个智能体：
- 有特定的角色和职责
- 可以独立思考和决策
- 能够与其他智能体协作
- 共同完成复杂任务

【核心设计模式】

1. 管道模式 (Pipeline)
   智能体按顺序执行，前一个的输出作为后一个的输入
   适合：任务分解明确、步骤清晰的场景
   
   Agent A → Agent B → Agent C → 结果

2. 并行模式 (Parallel)
   多个智能体同时处理不同方面
   适合：多维度分析、需要不同专业视角的场景
   
      ┌→ Agent A ┐
   输入 ┼→ Agent B ┼→ 汇总 → 结果
      └→ Agent C ┘

3. 层级模式 (Hierarchical)
   主管智能体分配任务，执行智能体具体处理
   适合：复杂任务分解、需要协调管理的场景
   
         主管 Agent
        /    |    \
   执行A   执行B   执行C
        \\    |    /
         汇总 Agent

4. 辩论模式 (Debate)
   多个智能体从不同角度讨论，最终达成共识
   适合：需要全面考虑、避免偏见的决策场景

【LangGraph 实现要点】

1. 状态管理 (State)
   - 使用 TypedDict 定义共享状态
   - 各节点可以读写状态
   - 状态在智能体间传递信息

2. 节点定义 (Node)
   - 每个智能体是一个节点
   - 节点函数接收状态，返回更新后的状态
   - 节点内可以调用 LLM 进行推理

3. 流程控制 (Edge)
   - 定义节点间的流转关系
   - 支持条件分支 (add_conditional_edges)
   - 可以创建循环和复杂流程
   
   条件分支示例：
   ```python
   workflow.add_conditional_edges(
       "reviewer",                    # 当前节点
       check_review_result,           # 判断函数
       {
           "approved": END,           # 通过 → 结束
           "rejected": "strategist",  # 不通过 → 返回修改
           "max_iterations": END,     # 达到最大迭代 → 强制结束
       }
   )
   ```

4. 工具集成 (Tool)
   - 智能体可以调用外部工具
   - 工具调用结果回到状态
   - 支持人机协作

【应用场景】

✅ 适合使用 Multi-Agent：
- 复杂任务需要多步骤处理
- 需要不同专业领域的知识
- 任务可以分解为独立子任务
- 需要多角度分析和验证

❌ 不适合使用 Multi-Agent：
- 简单直接的问答
- 单步骤即可完成的任务
- 对延迟敏感的场景
- 资源受限的环境
"""
    print(concepts)


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 Multi-Agent 多智能体系统示例")
    print("=" * 70)
    
    # 检查 API Key
    if not check_api_key("openai") and not check_api_key("qwen"):
        print("\n⚠️  未配置 API Key，将尝试使用 Ollama")
        print("   注意: Ollama 可能响应较慢或质量有限")
    
    try:
        # 演示1: 多智能体协作
        demo_multi_agent_collaboration()
        
        # 演示2: 智能体辩论
        demo_agent_debate()
        
        # 演示3: 层级智能体
        demo_hierarchical_agents()
        
        # 打印概念说明
        print_concepts()
        
        print("\n" + "=" * 70)
        print("✅ Multi-Agent 示例运行完成！")
        print("=" * 70)
        print("""
💡 学习建议：
1. 阅读代码了解多智能体系统的实现方式
2. 尝试修改智能体的角色和提示词
3. 添加新的智能体节点，扩展工作流程
4. 尝试不同的任务类型，观察协作效果
5. 探索更复杂的流程控制（条件分支、循环等）

📚 推荐学习资源：
- LangGraph 官方文档: https://langchain-ai.github.io/langgraph/
- 多智能体系统设计模式
- AutoGen 框架（微软的多智能体框架）
""")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

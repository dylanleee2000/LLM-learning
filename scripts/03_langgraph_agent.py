"""
示例 3: LangGraph Agent
LangGraph Agent 示例，演示如何使用工具的智能体
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_init import get_llm
from core.config import check_api_key
from agents.base_agent import SimpleAgent
from agents.skills import example_skill


def demo_simple_agent():
    """演示简单 Agent（无工具）"""
    print("\n" + "=" * 60)
    print("🤖 演示 1: 简单 Agent（无工具）")
    print("=" * 60)

    provider = "openai" if check_api_key("openai") else "ollama"
    llm = get_llm(provider=provider, temperature=0.7)

    system_prompt = """你是一个乐于助人的 AI 助手。
    回答要简洁明了，如果是技术问题，请给出代码示例。"""

    agent = SimpleAgent(llm, system_prompt=system_prompt)

    questions = [
        "Python 中的列表推导式是什么？给个例子",
        "如何读取一个文件的所有行？",
    ]

    for q in questions:
        print(f"\n👤 用户: {q}")
        response = agent.run(q)
        print(f"🤖 Agent: {response[:300]}..." if len(response) > 300 else f"🤖 Agent: {response}")


def demo_with_tools():
    """演示带工具的 Agent"""
    print("\n" + "=" * 60)
    print("🛠️  演示 2: Agent + 工具")
    print("=" * 60)

    provider = "openai" if check_api_key("openai") else "ollama"

    # 使用支持工具调用的模型
    try:
        llm = get_llm(provider=provider, model="gpt-3.5-turbo", temperature=0.7)
    except:
        llm = get_llm(provider=provider, temperature=0.7)

    # 获取工具
    tools = example_skill.get_tools()
    print(f"\n📦 可用工具: {[t.name for t in tools]}")
    for t in tools:
        print(f"   - {t.name}: {t.description}")

    # 手动演示工具调用
    print("\n🔧 工具调用演示:")

    test_inputs = [
        ("get_current_time", ""),
        ("calculate", "15 * 23 + 7"),
        ("search_knowledge", "python"),
    ]

    for tool_name, input_data in test_inputs:
        tool = next((t for t in tools if t.name == tool_name), None)
        if tool:
            print(f"\n   调用: {tool_name}({input_data!r})")
            result = tool.func(input_data)
            print(f"   结果: {result}")

    # Agent 对话演示
    print("\n💬 Agent 对话演示:")
    print("   (注意: 完整 Agent 工具调用需要支持 function calling 的模型)")

    # 简单模拟 Agent 行为
    system_prompt = f"""你是一个智能助手，可以使用以下工具:
    
    {chr(10).join([f"- {t.name}: {t.description}" for t in tools])}
    
    如果用户请求需要使用工具，请说明你会调用哪个工具。
    """

    agent = SimpleAgent(llm, system_prompt=system_prompt)

    questions = [
        "现在几点了？",
        "帮我计算 123 * 456",
        "什么是 LangChain？",
    ]

    for q in questions:
        print(f"\n👤 用户: {q}")
        response = agent.run(q)
        print(f"🤖 Agent: {response}")


def demo_agent_concept():
    """演示 Agent 概念和工作流程"""
    print("\n" + "=" * 60)
    print("📚 演示 3: Agent 概念说明")
    print("=" * 60)

    explanation = """
    Agent (智能体) 是一种能够自主决策和执行任务的 AI 系统。
    
    核心特点:
    1. 推理能力 - 理解任务并规划步骤
    2. 工具使用 - 调用外部工具获取信息或执行操作
    3. 记忆能力 - 维护对话历史和上下文
    4. 自主决策 - 根据情况决定下一步行动
    
    典型工作流程:
    ┌─────────────┐
    │  接收任务    │
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │  分析需求    │
    └──────┬──────┘
           ▼
    ┌─────────────┐     需要工具?     ┌─────────────┐
    │  是否需要    │ ───────────────▶ │  调用工具    │
    │  使用工具?   │ ◀─────────────── │  获取结果    │
    └──────┬──────┘     是            └─────────────┘
           │ 否
           ▼
    ┌─────────────┐
    │  生成回答    │
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │  完成任务    │
    └─────────────┘
    
    本项目的 Agent 框架基于 LangGraph:
    - 使用 StateGraph 定义工作流
    - 支持条件分支和循环
    - 可扩展的工具系统
    - 支持流式输出
    """
    print(explanation)


def main():
    print("=" * 60)
    print("🚀 LangGraph Agent 示例")
    print("=" * 60)

    # 检查 API Key
    if not check_api_key("openai") and not check_api_key("qwen"):
        print("\n⚠️  未配置 API Key，将尝试使用 Ollama")
        print("   注意: Ollama 可能不支持完整的工具调用功能")

    try:
        demo_simple_agent()
        demo_with_tools()
        demo_agent_concept()

        print("\n" + "=" * 60)
        print("✅ Agent 示例运行完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("   - 查看 agents/base_agent.py 了解 Agent 实现")
        print("   - 查看 agents/skills/example_skill.py 了解如何创建工具")
        print("   - 尝试修改示例，添加自己的工具！")

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

"""
示例 6: Function Call 核心概念
演示 LLM 如何通过 Function Call 调用外部工具，完成"感知→决策→执行→回答"闭环
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# 禁用 LangSmith 追踪，避免 SSL/403 报错干扰输出
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from core.llm_init import get_llm
from core.config import check_api_key


# ============================================================
# 第一步：用 @tool 定义工具（这是 Function Call 的基础）
# ============================================================

@tool
def get_current_time() -> str:
    """获取当前日期和时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate(expression: str) -> str:
    """计算数学表达式，如 '2 + 3' 或 '15 * 23'"""
    try:
        result = eval(expression)  # 教学用途，生产环境请用安全方式
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气（模拟数据）"""
    weather_data = {
        "北京": "晴天, 22°C, 微风",
        "上海": "多云, 25°C, 东南风3级",
        "深圳": "阵雨, 28°C, 南风2级",
    }
    return weather_data.get(city, f"{city}: 暂无天气数据")


# 收集所有工具
tools = [get_current_time, calculate, get_weather]


# ============================================================
# 第二步：获取支持 Function Call 的 LLM
# ============================================================

def get_llm_with_tools():
    """获取支持 function calling 的 LLM，按优先级尝试各 provider"""
    providers = []
    if check_api_key("qwen"):
        providers.append(("qwen", "qwen-turbo"))
    if check_api_key("mimo"):
        providers.append(("mimo", "mimo-v2-pro"))
    if check_api_key("openai"):
        providers.append(("openai", "gpt-3.5-turbo"))

    for provider, model in providers:
        try:
            llm = get_llm(provider=provider, model=model, temperature=0)
            llm_with_tools = llm.bind_tools(tools)
            print(f"✅ 使用 {provider} ({model})，支持 Function Call")
            return llm_with_tools
        except Exception:
            continue

    raise RuntimeError("无可用 API Key，请配置 .env 中的 DASHSCOPE_API_KEY / MIMO_API_KEY / OPENAI_API_KEY")


# ============================================================
# Demo 1: LLM 如何决策——观察 tool_calls 结构
# ============================================================

def demo1_llm_decision():
    """观察 LLM 在收到问题后，如何决定调用哪个工具"""
    print("\n" + "=" * 60)
    print("Demo 1: LLM 决策——它怎么知道该调用哪个工具？")
    print("=" * 60)

    llm_with_tools = get_llm_with_tools()

    question = "北京今天天气怎么样？"
    print(f"\n👤 用户: {question}")
    print("\n📤 LLM 收到问题后，不是直接回答，而是返回一个 tool_calls:")

    ai_msg = llm_with_tools.invoke([HumanMessage(content=question)])

    print(f"   content: {ai_msg.content!r}")
    print(f"   tool_calls: {json.dumps(ai_msg.tool_calls, ensure_ascii=False, indent=6)}")

    print("\n💡 关键理解:")
    print("   - LLM 不是'直接回答'，而是返回 tool_calls 表示'我需要调用工具'")
    print("   - tool_calls 包含: 工具名(name) + 参数(args) + 调用ID(id)")
    print("   - bind_tools() 的作用：把工具的 schema 告诉 LLM，让它知道能调什么")


# ============================================================
# Demo 2: 完整闭环——执行工具并把结果回传 LLM
# ============================================================

def demo2_full_loop():
    """完成一次完整的 Function Call 闭环：提问→决策→执行→回传→回答"""
    print("\n" + "=" * 60)
    print("Demo 2: 完整闭环——从提问到最终回答")
    print("=" * 60)

    llm_with_tools = get_llm_with_tools()
    question = "现在几点了？帮我算一下 123 * 456"

    print(f"\n👤 用户: {question}")

    # Step 1: LLM 决策
    print("\n[Step 1] LLM 决策...")
    ai_msg = llm_with_tools.invoke([HumanMessage(content=question)])

    if not ai_msg.tool_calls:
        print("   LLM 没有调用工具，直接回答了:", ai_msg.content)
        return

    for tc in ai_msg.tool_calls:
        print(f"   → 决定调用: {tc['name']}({tc['args']})")

    # Step 2: 执行工具
    print("\n[Step 2] 执行工具...")
    tool_map = {t.name: t for t in tools}
    tool_messages = []
    for tc in ai_msg.tool_calls:
        result = tool_map[tc["name"]].invoke(tc["args"])
        print(f"   → {tc['name']} 返回: {result}")
        tool_messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # Step 3: 把工具结果回传 LLM，让它生成最终回答
    print("\n[Step 3] 将工具结果回传 LLM，生成最终回答...")
    messages = [HumanMessage(content=question), ai_msg] + tool_messages
    final = llm_with_tools.invoke(messages)
    print(f"🤖 LLM: {final.content}")

    print("\n💡 关键理解:")
    print("   - 完整流程: 用户提问 → LLM返回tool_calls → 执行工具 → ToolMessage回传 → LLM最终回答")
    print("   - ToolMessage 必须携带 tool_call_id，LLM 靠它匹配哪次调用的结果")


# ============================================================
# Demo 3: 多轮循环——Agent 的核心模式
# ============================================================

def demo3_agent_loop():
    """用 while 循环处理多轮工具调用，这是 Agent 的核心模式"""
    print("\n" + "=" * 60)
    print("Demo 3: Agent 循环——while 循环驱动多轮调用")
    print("=" * 60)

    llm_with_tools = get_llm_with_tools()
    question = "上海天气如何？如果下雨提醒我带伞"
    print(f"\n👤 用户: {question}")

    # Agent 循环的核心：不断让 LLM 决策，直到它不再调用工具
    messages = [HumanMessage(content=question)]
    tool_map = {t.name: t for t in tools}
    step = 0

    while True:
        step += 1
        print(f"\n[第{step}轮] LLM 思考...")
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        # 没有 tool_calls 说明 LLM 已经得到足够信息，可以回答了
        if not ai_msg.tool_calls:
            print(f"🤖 LLM: {ai_msg.content}")
            break

        # 有 tool_calls，执行工具并把结果加入消息列表
        for tc in ai_msg.tool_calls:
            print(f"   → 调用: {tc['name']}({tc['args']})")
            result = tool_map[tc["name"]].invoke(tc["args"])
            print(f"   → 结果: {result}")
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    print("\n💡 关键理解:")
    print("   - while True 循环 = Agent 的'思考循环'")
    print("   - LLM 有 tool_calls → 执行工具，继续循环")
    print("   - LLM 无 tool_calls → 它已准备好回答，退出循环")
    print("   - 这就是 LangGraph Agent、OpenAI Assistants 等框架的底层逻辑")


# ============================================================

def main():
    print("=" * 60)
    print("🔧 Function Call 核心概念演示")
    print("=" * 60)
    print("\nFunction Call 是 LLM 调用外部工具的标准机制：")
    print("  1. LLM 不是直接回答，而是返回 tool_calls（工具名+参数）")
    print("  2. 开发者执行工具，将结果通过 ToolMessage 回传")
    print("  3. LLM 根据工具结果生成最终回答")
    print("  4. 用 while 循环处理多轮调用，这就是 Agent 的核心模式")

    try:
        demo1_llm_decision()   # 观察决策
        demo2_full_loop()      # 完整闭环
        demo3_agent_loop()     # Agent 循环

        print("\n" + "=" * 60)
        print("✅ Function Call 核心概念演示完成！")
        print("=" * 60)
        print("\n🧠 回顾核心知识点:")
        print("   @tool        → 定义工具（名字、描述、参数）")
        print("   bind_tools   → 把工具 schema 告诉 LLM")
        print("   tool_calls   → LLM 返回的调用指令（name + args + id）")
        print("   ToolMessage  → 把工具执行结果回传给 LLM")
        print("   while 循环   → Agent 多轮调用的核心模式")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

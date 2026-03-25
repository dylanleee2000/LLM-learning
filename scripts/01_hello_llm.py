"""
示例 1: Hello LLM
基础 LLM 调用示例，演示如何初始化模型并进行简单对话
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_init import get_llm
from core.config import check_api_key


def main():
    print("=" * 50)
    print("🤖 Hello LLM - 基础 LLM 调用示例")
    print("=" * 50)

    # 选择模型提供商
    providers = ["openai", "qwen", "ollama"]
    print("\n支持的模型提供商:")
    for i, p in enumerate(providers, 1):
        has_key = check_api_key(p) if p != "ollama" else True
        status = "✓" if has_key else "✗"
        print(f"  {i}. {p} {status}")

    # 默认使用 openai
    provider = "qwen"

    # 检查 API Key
    if not check_api_key(provider):
        print(f"\n⚠️  未配置 {provider} 的 API Key")
        print(f"请在 .env 文件中设置 {provider.upper()}_API_KEY")
        print("\n尝试使用 Ollama (本地模型)...")
        provider = "ollama"

    try:
        # 初始化 LLM
        print(f"\n🔄 正在初始化 {provider} 模型...")
        llm = get_llm(provider=provider, temperature=0.7)
        print(f"✓ 模型初始化成功")

        # 简单对话
        question = "你好，请用一句话介绍一下你自己"
        print(f"\n👤 用户: {question}")
        print("\n🤖 AI 思考中...")

        response = llm.invoke(question)
        print(f"\n🤖response {response}")
        answer = response.content if hasattr(response, 'content') else str(response)

        print(f"\n💬 AI: {answer}")

        # 多轮对话示例
        print("\n" + "-" * 50)
        print("多轮对话示例:")
        print("-" * 50)

        questions = [
            "Python 有什么特点？",
            "那它和 JavaScript 有什么区别？",
        ]

        from langchain_core.messages import HumanMessage, AIMessage

        messages = []
        for q in questions:
            print(f"\n👤 用户: {q}")
            messages.append(HumanMessage(content=q))

            response = llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            messages.append(AIMessage(content=answer))

            print(f"💬 AI: {answer[:200]}..." if len(answer) > 200 else f"💬 AI: {answer}")

        print("\n" + "=" * 50)
        print("✅ 示例运行完成！")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n排查建议:")
        print("1. 检查 .env 文件中的 API Key 是否正确")
        print("2. 确认网络连接正常")
        print("3. 如果使用 Ollama，确认本地服务已启动")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

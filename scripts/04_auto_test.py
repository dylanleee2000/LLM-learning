"""
示例 4: Auto Test
使用 LLM 生成测试用例的示例
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm_init import get_llm
from core.config import check_api_key
from core.prompt_templates import get_test_generation_prompt


# 示例代码：需要测试的函数
EXAMPLE_CODE = '''
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    计算折扣后的价格
    
    Args:
        price: 原价
        discount_rate: 折扣率 (0-1)
    
    Returns:
        折扣后价格
    """
    if price < 0:
        raise ValueError("价格不能为负数")
    if not 0 <= discount_rate <= 1:
        raise ValueError("折扣率必须在 0-1 之间")
    
    return price * (1 - discount_rate)


def is_valid_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        是否有效
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
'''


def demo_test_generation():
    """演示测试用例生成"""
    print("\n" + "=" * 60)
    print("🧪 演示 1: LLM 生成测试用例")
    print("=" * 60)

    provider = "openai" if check_api_key("openai") else "ollama"
    llm = get_llm(provider=provider, temperature=0.3)  # 低温度，更确定性的输出

    print("\n📄 待测试代码:")
    print(EXAMPLE_CODE)

    print("\n🤖 正在生成测试用例...")
    print("-" * 60)

    # 使用 Prompt 模板
    prompt_template = get_test_generation_prompt()
    prompt = prompt_template.format(code=EXAMPLE_CODE)

    response = llm.invoke(prompt)
    generated_tests = response.content if hasattr(response, 'content') else str(response)

    print(generated_tests)
    print("-" * 60)


def demo_code_review():
    """演示代码审查"""
    print("\n" + "=" * 60)
    print("🔍 演示 2: LLM 代码审查")
    print("=" * 60)

    provider = "openai" if check_api_key("openai") else "ollama"
    llm = get_llm(provider=provider, temperature=0.3)

    code_to_review = '''
def get_user_data(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
    return cursor.fetchone()
'''

    print("\n📄 待审查代码:")
    print(code_to_review)

    print("\n🤖 代码审查意见:")
    print("-" * 60)

    from core.prompt_templates import get_code_review_prompt
    prompt_template = get_code_review_prompt()
    prompt = prompt_template.format(code=code_to_review)

    response = llm.invoke(prompt)
    review = response.content if hasattr(response, 'content') else str(response)

    print(review)
    print("-" * 60)


def demo_test_execution():
    """演示测试执行"""
    print("\n" + "=" * 60)
    print("▶️  演示 3: 测试执行")
    print("=" * 60)

    # 实际执行测试
    print("\n运行手动编写的测试:")

    def calculate_discount(price: float, discount_rate: float) -> float:
        if price < 0:
            raise ValueError("价格不能为负数")
        if not 0 <= discount_rate <= 1:
            raise ValueError("折扣率必须在 0-1 之间")
        return price * (1 - discount_rate)

    # 测试用例
    test_cases = [
        ("正常折扣", lambda: calculate_discount(100, 0.2), 80.0),
        ("零折扣", lambda: calculate_discount(100, 0), 100.0),
        ("免费", lambda: calculate_discount(100, 1), 0.0),
    ]

    passed = 0
    failed = 0

    for name, test_func, expected in test_cases:
        try:
            result = test_func()
            if abs(result - expected) < 0.001:
                print(f"  ✓ {name}: 通过")
                passed += 1
            else:
                print(f"  ✗ {name}: 失败 (期望 {expected}, 实际 {result})")
                failed += 1
        except Exception as e:
            print(f"  ✗ {name}: 异常 - {e}")
            failed += 1

    # 边界情况测试
    print("\n边界情况测试:")

    boundary_cases = [
        ("负数价格", lambda: calculate_discount(-10, 0.2), ValueError),
        ("折扣率过大", lambda: calculate_discount(100, 1.5), ValueError),
        ("负折扣率", lambda: calculate_discount(100, -0.1), ValueError),
    ]

    for name, test_func, expected_error in boundary_cases:
        try:
            test_func()
            print(f"  ✗ {name}: 应该抛出 {expected_error.__name__}")
            failed += 1
        except expected_error:
            print(f"  ✓ {name}: 正确抛出异常")
            passed += 1
        except Exception as e:
            print(f"  ✗ {name}: 异常类型错误 - {e}")
            failed += 1

    print(f"\n测试结果: {passed} 通过, {failed} 失败")


def demo_concept():
    """演示自动化测试概念"""
    print("\n" + "=" * 60)
    print("📚 LLM 辅助测试的概念")
    print("=" * 60)

    concept = """
    LLM 可以在软件测试中发挥多种作用:
    
    1. 测试用例生成
       - 分析代码自动生成测试用例
       - 覆盖正常情况和边界情况
       - 减少人工编写测试的工作量
    
    2. 测试代码补全
       - 根据函数签名生成测试框架
       - 补充断言和测试数据
    
    3. 测试解释
       - 解释失败的测试用例
       - 分析失败原因并提供修复建议
    
    4. 测试文档生成
       - 从测试代码生成测试文档
       - 描述测试覆盖范围
    
    5. 变异测试
       - 生成代码变体测试测试用例的健壮性
    
    最佳实践:
    - LLM 生成的测试需要人工审查
    - 结合传统测试方法使用
    - 对关键代码仍需人工编写测试
    - 使用 LLM 生成测试草稿，人工完善
    """
    print(concept)


def main():
    print("=" * 60)
    print("🧪 Auto Test - 自动化测试示例")
    print("=" * 60)

    if not check_api_key("openai") and not check_api_key("qwen"):
        print("\n⚠️  未配置 API Key，将尝试使用 Ollama")

    try:
        demo_test_generation()
        demo_code_review()
        demo_test_execution()
        demo_concept()

        print("\n" + "=" * 60)
        print("✅ 自动化测试示例运行完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

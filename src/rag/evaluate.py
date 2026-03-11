import json
from .app import ask_edin

# Define test cases: A mix of relevant and "out-of-bounds" questions
test_cases = [
    {
        "query": "what is the cutoff for bc-d category?",
        "expected_type": "answered"
    },
    {
        "query": "what is IIT Bombay cutoff?",
        "expected_type": "rejected"
    },
    {
        "query": "who is the prime minister of india?",
        "expected_type": "rejected"
    }
]

def run_evaluation():
    print("\n🚀 --- Running EDin System Evaluation --- 🚀\n")

    correct = 0

    for i, test in enumerate(test_cases, 1):
        # Run the actual RAG pipeline
        result = ask_edin(test["query"])

        # Determine if the system gave a real answer or triggered the Safety Gate
        result_type = "rejected" if result["confidence"] == 0.0 else "answered"

        # Check against our expectations
        passed = result_type == test["expected_type"]

        print(f"Test {i}: {test['query']}")
        print(f"Expected: {test['expected_type']} | Got: {result_type}")
        
        if passed:
            print("✅ STATUS: PASS")
            correct += 1
        else:
            print("❌ STATUS: FAIL")
            
        print("-" * 50)

    # Final summary for your Progress Report
    print(f"\n🎯 Final Score: {correct}/{len(test_cases)} passed")
    print(f"Success Rate: {round((correct/len(test_cases)) * 100, 2)}%\n")

if __name__ == "__main__":
    run_evaluation()
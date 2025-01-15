from openai import OpenAI
from openai.types.chat import ChatCompletion
from dataclasses import dataclass
from typing import Optional

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    reasoning_tokens: Optional[int] = None

@dataclass
class O1Response:
    content: str
    token_usage: TokenUsage
    cost: float

def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate the cost of API usage based on o1 model pricing.
    
    Args:
        prompt_tokens: Number of input tokens
        completion_tokens: Number of completion tokens (including reasoning)
    
    Returns:
        Total cost in USD
    """
    # Pricing per 1M tokens
    INPUT_PRICE_PER_M = 15.0
    OUTPUT_PRICE_PER_M = 60.0
    
    # Convert to millions and calculate
    input_cost = (prompt_tokens / 1_000_000) * INPUT_PRICE_PER_M
    output_cost = (completion_tokens / 1_000_000) * OUTPUT_PRICE_PER_M
    
    return input_cost + output_cost

def query_o1(messages: list[dict[str, str]], reasoning_effort: str = "low") -> O1Response:
    """Query the o1 model and return the response with token usage and cost.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        reasoning_effort: Level of reasoning effort ("low", "medium", "high")
    
    Returns:
        O1Response containing the model's response, token usage, and cost
    """
    client = OpenAI()
    
    response: ChatCompletion = client.chat.completions.create(
        model="o1",
        messages=messages,
        response_format={"type": "text"},
        reasoning_effort=reasoning_effort
    )
    
    # Extract token usage
    usage = response.usage
    token_usage = TokenUsage(
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
        reasoning_tokens=usage.completion_tokens_details.reasoning_tokens if usage.completion_tokens_details else None
    )
    
    # Calculate cost
    cost = calculate_cost(token_usage.prompt_tokens, token_usage.completion_tokens)
    
    return O1Response(
        content=response.choices[0].message.content,
        token_usage=token_usage,
        cost=cost
    )

def main():
    # Test message asking for a joke
    messages = [
        {"role": "user", "content": "Tell me a short joke about programming. 最好给我惊喜."}
    ]
    
    print("Sending request to OpenAI API...")
    response = query_o1(messages)
    
    print("\nJoke from o1:")
    print(response.content)
    
    print("\nToken Usage:")
    print(f"Input tokens: {response.token_usage.prompt_tokens}")
    print(f"Output tokens: {response.token_usage.completion_tokens}")
    if response.token_usage.reasoning_tokens is not None:
        print(f"  - Including reasoning tokens: {response.token_usage.reasoning_tokens}")
    print(f"Total tokens: {response.token_usage.total_tokens}")
    
    print(f"\nEstimated cost: ${response.cost:.6f}")

if __name__ == "__main__":
    main() 
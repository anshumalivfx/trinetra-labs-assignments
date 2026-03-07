# Mistral AI Integration Guide

This project now uses **Mistral AI** instead of OpenAI for powering the AI agents. Mistral AI provides free access to powerful open-source language models.

## 🆓 Getting a Free Mistral AI API Key

### Step 1: Create an Account
1. Visit [https://console.mistral.ai/](https://console.mistral.ai/)
2. Sign up for a free account using your email or GitHub
3. Confirm your email address

### Step 2: Generate API Key
1. Once logged in, navigate to the **API Keys** section
2. Click on **"Create new key"**
3. Give your key a name (e.g., "AI Orchestration System")
4. Copy the generated API key (starts with `xxxx...`)
5. Store it securely - you won't be able to see it again!

### Step 3: Configure Your Application
Add your API key to the `.env` file:
```bash
MISTRAL_API_KEY=your-mistral-api-key-here
```

## 📊 Available Free Models

Mistral AI offers several free open-source models:

### 1. **open-mixtral-8x7b** (Default)
- **Best for**: General purpose tasks
- **Parameters**: 8x7B (Mixture of Experts)
- **Context window**: 32K tokens
- **Use cases**: Document analysis, email composition, general reasoning

### 2. **open-mistral-7b**
- **Best for**: Fast, lightweight tasks
- **Parameters**: 7B
- **Context window**: 32K tokens
- **Use cases**: Simple text generation, quick responses

### 3. **mistral-small-latest**
- **Best for**: High-quality responses
- **Parameters**: Moderate size
- **Context window**: 32K tokens
- **Use cases**: Production workloads, complex reasoning

### 4. **open-mixtral-8x22b**
- **Best for**: Most demanding tasks
- **Parameters**: 8x22B (Mixture of Experts)
- **Context window**: 64K tokens
- **Use cases**: Complex analysis, advanced reasoning

## ⚙️ Changing the Model

To use a different Mistral model, update the `MISTRAL_MODEL` setting in your `.env` file:

```bash
# Option 1: Fast and lightweight
MISTRAL_MODEL=open-mistral-7b

# Option 2: Balanced (Default)
MISTRAL_MODEL=open-mixtral-8x7b

# Option 3: High quality
MISTRAL_MODEL=mistral-small-latest

# Option 4: Most powerful
MISTRAL_MODEL=open-mixtral-8x22b
```

## 📚 Documentation Links

- **Official Docs**: [https://docs.mistral.ai/](https://docs.mistral.ai/)
- **API Reference**: [https://docs.mistral.ai/api/](https://docs.mistral.ai/api/)
- **Model Overview**: [https://docs.mistral.ai/getting-started/models/](https://docs.mistral.ai/getting-started/models/)
- **Python Client**: [https://github.com/mistralai/client-python](https://github.com/mistralai/client-python)
- **LangChain Integration**: [https://python.langchain.com/docs/integrations/chat/mistralai](https://python.langchain.com/docs/integrations/chat/mistralai)

## 🔑 Key Features of Mistral AI

### Free Tier Benefits
- ✅ No credit card required for initial testing
- ✅ Access to powerful open-source models
- ✅ Generous rate limits for development
- ✅ Same API interface as commercial models

### Technical Advantages
- **Fast inference**: Optimized for low latency
- **Large context windows**: 32K-64K tokens
- **Multilingual**: Support for multiple languages
- **JSON mode**: Native support for structured outputs
- **Function calling**: Tool use and agent capabilities

## 🚀 Rate Limits

Free tier rate limits (as of March 2026):
- **Requests**: Up to 1 request per second
- **Tokens**: Subject to fair usage policy
- **Concurrent requests**: Up to 2

For higher limits, consider upgrading to a paid plan.

## 💡 Tips for Best Results

### 1. Temperature Settings
- **0.1-0.3**: Factual, deterministic responses (email validation)
- **0.5-0.7**: Balanced creativity (email composition)
- **0.8-1.0**: Highly creative outputs

### 2. Token Optimization
- Mistral models are efficient with tokens
- Use concise prompts for better performance
- The default model `open-mixtral-8x7b` offers good balance

### 3. Error Handling
The application includes automatic retry logic for:
- Rate limit errors (429)
- Temporary service issues (503)
- Network timeouts

## 🆚 Mistral AI vs OpenAI

| Feature | Mistral AI (Free) | OpenAI (Paid) |
|---------|-------------------|---------------|
| Cost | Free tier available | Pay per token |
| Models | Open-source | Proprietary |
| Context | 32K-64K tokens | 4K-128K tokens |
| Speed | Fast | Very fast |
| Quality | Excellent | Excellent |
| Privacy | EU-based, GDPR-compliant | US-based |

## 🔧 Troubleshooting

### API Key Issues
```bash
# Error: Invalid API key
# Solution: Verify your key in .env file
cat .env | grep MISTRAL_API_KEY
```

### Rate Limit Errors
```bash
# Error: Rate limit exceeded
# Solution: The system has automatic retry logic with exponential backoff
# If persistent, consider upgrading your Mistral plan
```

### Model Not Found
```bash
# Error: Model not available
# Solution: Use one of the supported free models:
#   - open-mistral-7b
#   - open-mixtral-8x7b (default)
#   - mistral-small-latest
#   - open-mixtral-8x22b
```

## 📞 Support

For Mistral AI specific issues:
- **Discord**: [https://discord.gg/mistralai](https://discord.gg/mistralai)
- **GitHub**: [https://github.com/mistralai](https://github.com/mistralai)
- **Documentation**: [https://docs.mistral.ai/](https://docs.mistral.ai/)

For application issues, see the main [README.md](README.md).

## 🎓 Next Steps

1. ✅ Get your free Mistral API key
2. ✅ Add it to your `.env` file
3. ✅ Choose your model (default: `open-mixtral-8x7b`)
4. ✅ Test the application with a sample PDF
5. ✅ Monitor performance and adjust settings as needed

Happy orchestrating! 🚀

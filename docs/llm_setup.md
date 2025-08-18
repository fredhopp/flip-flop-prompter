# LLM Integration Setup Guide

FlipFlopPrompt now supports LLM-powered prompt refinement for better, more cohesive prompts. This guide will help you set up either Ollama (local, free) or OpenAI API (cloud-based).

## Quick Start

### Option 1: Ollama (Recommended - Local & Free)

1. **Install Ollama**:
   ```bash
   # Windows (using winget)
   winget install Ollama.Ollama
   
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Download a model**:
   ```bash
   # Llama 3.1 8B (recommended - good balance of quality/speed)
   ollama pull llama3.1:8b
   
   # Or Mistral 7B (faster, still good quality)
   ollama pull mistral:7b
   ```

4. **Test the setup**:
   ```bash
   python main.py --list-models
   ```
   You should see "✓ LLM Available: OllamaProvider" in the output.

### Option 2: OpenAI API (Cloud-based)

1. **Get an API key**:
   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key

2. **Set the environment variable**:
   ```bash
   # Windows
   set OPENAI_API_KEY=your_api_key_here
   
   # macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Test the setup**:
   ```bash
   python main.py --list-models
   ```
   You should see "✓ LLM Available: OpenAIProvider" in the output.

## How It Works

### Before LLM Integration
```
Raw Input:
- Environment: hotel lobby
- Subjects: 20yo man
- Action: standing

Output: "Scene: hotel lobby, Characters: 20yo man, Action: standing, High quality, cinematic, professional lighting"
```

### After LLM Integration
```
Raw Input:
- Environment: hotel lobby
- Subjects: 20yo man
- Action: standing

Output: "A cinematic scene in an elegant hotel lobby where a young man in his twenties stands confidently, bathed in warm, professional lighting that creates a sophisticated atmosphere. The composition captures the grandeur of the space while focusing on the subject's poised demeanor."
```

## Model-Specific Optimization

The LLM is trained with specific guidelines for each model:

### Seedream 3.0
- Detailed, cinematic descriptions
- Technical film terminology
- Camera movements and angles
- Professional lighting emphasis

### Google Veo
- Natural, conversational language
- Scene composition focus
- Emotional context
- Visual quality emphasis

### Stability AI Flux
- Artistic and creative elements
- Stylized language
- Visual aesthetics focus
- Creative metaphors

### Wan
- Realistic and natural scenes
- Human interactions emphasis
- Authentic descriptions
- Clear, straightforward language

### Hailuo
- Comprehensive descriptions
- Technical precision
- Multiple visual layers
- Quality specifications

## Configuration

### Customizing Ollama Settings

You can modify the Ollama configuration in `src/core/llm_integration.py`:

```python
class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        # Change model_name to use different models
        # Change base_url if Ollama runs on different port
```

### Customizing OpenAI Settings

```python
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        # Change model to use different OpenAI models
        # Options: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
```

## Troubleshooting

### Ollama Issues

**"Ollama not found"**:
```bash
# Check if Ollama is installed
ollama --version

# If not installed, follow installation steps above
```

**"Model not found"**:
```bash
# List available models
ollama list

# Pull the required model
ollama pull llama3.1:8b
```

**"Connection refused"**:
```bash
# Start Ollama service
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

### OpenAI Issues

**"API key not found"**:
```bash
# Check environment variable
echo $OPENAI_API_KEY  # Linux/macOS
echo %OPENAI_API_KEY% # Windows

# Set it if missing
export OPENAI_API_KEY=your_key_here
```

**"Rate limit exceeded"**:
- Wait a few minutes and try again
- Consider using Ollama for unlimited usage

### Performance Tips

1. **Ollama Performance**:
   - Use `llama3.1:8b` for good balance
   - Use `mistral:7b` for faster responses
   - Ensure adequate RAM (8GB+ recommended)

2. **OpenAI Performance**:
   - Use `gpt-4o-mini` for cost efficiency
   - Use `gpt-4o` for best quality
   - Monitor API usage to control costs

## Fallback Behavior

If no LLM provider is available, FlipFlopPrompt automatically falls back to the basic model adapters. You'll still get functional prompts, just without the LLM refinement.

## Cost Considerations

- **Ollama**: Completely free, runs locally
- **OpenAI**: ~$0.15 per 1K tokens (roughly $0.01-0.05 per prompt)

## Next Steps

1. Set up either Ollama or OpenAI API
2. Test with `python main.py --list-models`
3. Try generating prompts to see the improvement
4. Customize model-specific guidelines if needed

The LLM integration will significantly improve prompt quality, especially for users who aren't experienced prompt engineers!
